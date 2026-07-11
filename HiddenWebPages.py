#!/usr/bin/env python3
import argparse
import csv
import json
import os
import queue
import re
import sys
import threading
import time
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

try:
    import requests
except ImportError:
    sys.exit("This script requires the 'requests' package: pip install requests")

DEFAULT_WORDLIST = ['admin', 'administrator', 'admin.php', 'admin.html', 'login', 'login.php', 'logout', 'signin', 'wp-admin', 'wp-login.php', 'wp-config.php', 'wp-content', 'wp-includes', 'xmlrpc.php', 'backup', 'backups', 'backup.zip', 'backup.tar.gz', 'backup.sql', 'db_backup.sql', 'site.zip', 'www.zip', 'config', 'config.php', 'config.json', 'config.yml', 'configuration', 'settings', 'settings.php', '.env', '.env.local', '.env.production', '.env.bak', '.git/HEAD', '.git/config', '.gitignore', '.svn/entries', '.htaccess', '.htpasswd', '.DS_Store', '.idea', '.vscode', 'test', 'test.php', 'testing', 'staging', 'dev', 'development', 'old', 'old_site', 'temp', 'tmp', 'hidden', 'private', 'internal', 'secret', 'beta', 'demo', 'sandbox', 'api', 'api/docs', 'api/v1', 'api/v2', 'graphql', 'swagger', 'swagger.json', 'swagger-ui', 'openapi.json', 'phpmyadmin', 'pma', 'adminer.php', 'server-status', 'server-info', 'console', 'debug', 'debug.php', 'phpinfo.php', 'info.php', '.well-known/security.txt', 'sitemap.xml.gz', 'sitemap_index.xml', 'sitemap1.xml', 'robots.txt.bak', 'web.config', 'crossdomain.xml', 'humans.txt', 'install', 'install.php', 'setup', 'setup.php', 'upload', 'uploads', 'files', 'file', 'assets', 'static', 'media', 'database', 'db', 'dump.sql', 'data.sql', 'db.sqlite3', 'logs', 'log', 'log.txt', 'error_log', 'access_log', 'debug.log', 'users.json', 'users.csv', 'users.sql', 'accounts.csv', 'credentials.txt', 'passwords.txt', 'secrets.json', 'id_rsa', '.ssh', 'docker-compose.yml', 'Dockerfile', 'package.json', 'composer.json', 'vendor', 'node_modules', 'cgi-bin', 'shell.php', 'cpanel', 'webmail', 'portal', 'dashboard', 'manage', 'management', 'moderator', 'super-admin', 'owner', 'status', 'health', 'metrics', 'actuator', 'version', 'changelog.txt', 'readme.txt', 'README.md', 'license.txt', 'TODO.txt', 'notes.txt']
DEFAULT_HEADERS = {'User-Agent': 'hidden-page-auditor/1.0 (site-owner self-audit tool)'}

@dataclass
class Finding:
    url: str
    source: str
    status: object = None
    linked: bool = False

@dataclass
class Discovery:
    findings: dict = field(default_factory=dict)

    def add(self, url, source, status=None):
        if url in self.findings:
            f = self.findings[url]
            if source not in f.source:
                f.source += f',{source}'
            if status is not None:
                f.status = status
        else:
            self.findings[url] = Finding(url=url, source=source, status=status)

def normalize_target(target):
    if not target.startswith(('http://', 'https://')):
        target = 'https://' + target
    parsed = urlparse(target)
    return f'{parsed.scheme}://{parsed.netloc}'

def get_robots(base_url, session, timeout):
    robots_url = urljoin(base_url + '/', 'robots.txt')
    (disallowed, sitemaps) = ([], [])
    try:
        resp = session.get(robots_url, timeout=timeout, headers=DEFAULT_HEADERS)
        if resp.status_code == 200:
            for line in resp.text.splitlines():
                line = line.strip()
                if line.lower().startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path and path != '/':
                        disallowed.append(path)
                elif line.lower().startswith('sitemap:'):
                    sitemaps.append(line.split(':', 1)[1].strip())
    except requests.RequestException as e:
        print(f'  [!] Could not fetch robots.txt: {e}')
    return (disallowed, sitemaps)

def parse_sitemap(url, session, timeout, seen=None, depth=0):
    if seen is None:
        seen = set()
    if url in seen or depth > 3:
        return []
    seen.add(url)
    urls = []
    try:
        resp = session.get(url, timeout=timeout, headers=DEFAULT_HEADERS)
        if resp.status_code != 200 or not resp.content.strip():
            return []
        root = ElementTree.fromstring(resp.content)
        tag = root.tag.lower()
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        if tag.endswith('sitemapindex'):
            for sm in root.findall('sm:sitemap/sm:loc', ns) or root.findall('.//{*}sitemap/{*}loc'):
                urls.extend(parse_sitemap(sm.text.strip(), session, timeout, seen, depth + 1))
        elif tag.endswith('urlset'):
            for loc in root.findall('sm:url/sm:loc', ns) or root.findall('.//{*}url/{*}loc'):
                if loc.text:
                    urls.append(loc.text.strip())
    except (requests.RequestException, ElementTree.ParseError) as e:
        print(f'  [!] Could not parse sitemap {url}: {e}')
    return urls

def get_wayback_urls(base_url, session, timeout, limit=2000):
    domain = urlparse(base_url).netloc
    cdx_url = f'https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original&collapse=urlkey&limit={limit}'
    try:
        resp = session.get(cdx_url, timeout=timeout, headers=DEFAULT_HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 1:
                return [row[0] for row in data[1:]]
    except (requests.RequestException, ValueError) as e:
        print(f'  [!] Could not query Wayback Machine: {e}')
    return []

def crawl_linked_pages(base_url, session, timeout, max_pages=30):
    domain = urlparse(base_url).netloc
    to_visit = [base_url]
    visited = set()
    linked = set()
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            resp = session.get(url, timeout=timeout, headers=DEFAULT_HEADERS)
        except requests.RequestException:
            continue
        if resp.status_code != 200:
            continue
        linked.add(url)
        for match in re.finditer('href=["\\\']([^"\\\'#]+)', resp.text):
            href = match.group(1)
            full = urljoin(url, href)
            if urlparse(full).netloc == domain:
                full = full.split('#')[0]
                linked.add(full)
                if full not in visited and len(visited) + len(to_visit) < max_pages:
                    to_visit.append(full)
    return linked

def dictionary_scan(base_url, wordlist, disallowed, ignore_robots, session, timeout, delay):
    results = []
    skipped = 0
    for path in wordlist:
        path = path.lstrip('/')
        if not ignore_robots and any((path.startswith(d.lstrip('/')) for d in disallowed)):
            skipped += 1
            continue
        url = urljoin(base_url + '/', path)
        try:
            resp = session.get(url, timeout=timeout, headers=DEFAULT_HEADERS, allow_redirects=False)
            if resp.status_code in (200, 201, 301, 302, 401, 403):
                results.append((url, resp.status_code))
        except requests.RequestException:
            pass
        time.sleep(delay)
    if skipped:
        print(f'  [i] Skipped {skipped} path(s) disallowed by robots.txt (use --ignore-robots to include them)')
    return results

def write_report(discovery, path):
    findings = sorted(discovery.findings.values(), key=lambda f: f.url)
    if path.endswith('.json'):
        with open(path, 'w') as f:
            json.dump([f.__dict__ for f in findings], f, indent=2)
    else:
        if not path.endswith('.csv'):
            path += '.csv'
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['url', 'source', 'status', 'linked_from_navigation'])
            for finding in findings:
                writer.writerow([finding.url, finding.source, finding.status, finding.linked])
    return path

def run_audit(target, output='hidden_pages_report.csv', delay=0.5, timeout=10.0, wordlist=None, no_dictionary=False, no_wayback=False, no_crawl=False, ignore_robots=False):
    base_url = normalize_target(target)
    session = requests.Session()
    discovery = Discovery()
    print(f'Auditing {base_url}\n')
    print('[1/5] Checking robots.txt ...')
    (disallowed, sitemap_hints) = get_robots(base_url, session, timeout)
    for path in disallowed:
        discovery.add(urljoin(base_url + '/', path.lstrip('/')), 'robots.txt')
    print(f'  Found {len(disallowed)} disallowed path(s), {len(sitemap_hints)} sitemap reference(s)')
    print('[2/5] Parsing sitemap(s) ...')
    sitemap_urls = set(sitemap_hints) | {urljoin(base_url + '/', 'sitemap.xml')}
    sitemap_pages = []
    for sm in sitemap_urls:
        sitemap_pages.extend(parse_sitemap(sm, session, timeout))
    for u in sitemap_pages:
        discovery.add(u, 'sitemap.xml')
    print(f'  Found {len(set(sitemap_pages))} page(s) in sitemap(s)')
    if not no_wayback:
        print('[3/5] Querying Wayback Machine archive ...')
        wb_urls = get_wayback_urls(base_url, session, timeout)
        for u in wb_urls:
            discovery.add(u, 'wayback')
        print(f'  Found {len(set(wb_urls))} archived URL(s)')
    else:
        print('[3/5] Skipped (Wayback lookup disabled)')
    if not no_dictionary:
        print('[4/5] Running light dictionary scan ...')
        wl = wordlist if wordlist else DEFAULT_WORDLIST
        hits = dictionary_scan(base_url, wl, disallowed, ignore_robots, session, timeout, delay)
        for (url, status) in hits:
            discovery.add(url, 'dictionary-scan', status)
        print(f'  Found {len(hits)} responsive path(s) out of {len(wl)} checked')
    else:
        print('[4/5] Skipped (dictionary scan disabled)')
    if not no_crawl:
        print('[5/5] Crawling site navigation to identify orphaned pages ...')
        linked = crawl_linked_pages(base_url, session, timeout)
        for (url, finding) in discovery.findings.items():
            finding.linked = url in linked
        print(f'  {len(linked)} page(s) reachable via normal navigation')
    else:
        print('[5/5] Skipped (navigation crawl disabled)')
    for finding in discovery.findings.values():
        if finding.status is None:
            try:
                resp = session.head(finding.url, timeout=timeout, headers=DEFAULT_HEADERS, allow_redirects=True)
                finding.status = resp.status_code
            except requests.RequestException:
                finding.status = 'unreachable'
    report_path = write_report(discovery, output)
    hidden = [f for f in discovery.findings.values() if not f.linked]
    print(f'\nDone. {len(discovery.findings)} total page(s) discovered, {len(hidden)} not linked from normal navigation ("hidden").')
    print(f'Full report written to {report_path}')
    return (discovery, report_path)

def cli_main(argv):
    parser = argparse.ArgumentParser(prog='hidden_page_finder.py', description='Find hidden/orphaned pages on a site you own or are authorized to audit.')
    parser.add_argument('target', help='Domain or URL to audit, e.g. example.com')
    parser.add_argument('--output', default='hidden_pages_report.csv', help='Report file (.csv or .json). Default: hidden_pages_report.csv')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay in seconds between dictionary-scan requests (default 0.5)')
    parser.add_argument('--timeout', type=float, default=10.0, help='Request timeout in seconds')
    parser.add_argument('--wordlist', help='Path to a custom wordlist file (one path per line)')
    parser.add_argument('--no-dictionary', action='store_true', help='Skip the dictionary scan')
    parser.add_argument('--no-wayback', action='store_true', help='Skip Wayback Machine lookup')
    parser.add_argument('--no-crawl', action='store_true', help='Skip crawling the homepage for linked pages (comparison step)')
    parser.add_argument('--ignore-robots', action='store_true', help='Also actively fetch paths disallowed by robots.txt (only use this on sites you own)')
    args = parser.parse_args(argv)
    wordlist = None
    if args.wordlist:
        with open(args.wordlist) as f:
            wordlist = [line.strip() for line in f if line.strip()]
    (discovery, report_path) = run_audit(args.target, output=args.output, delay=args.delay, timeout=args.timeout, wordlist=wordlist, no_dictionary=args.no_dictionary, no_wayback=args.no_wayback, no_crawl=args.no_crawl, ignore_robots=args.ignore_robots)
    hidden = [f for f in discovery.findings.values() if not f.linked]
    if hidden:
        print('\nTop hidden findings:')
        for f in sorted(hidden, key=lambda x: str(x.status))[:15]:
            print(f'  [{f.status}] {f.url}  (source: {f.source})')

class QueueWriter:

    def __init__(self, q):
        self.q = q

    def write(self, msg):
        if msg:
            self.q.put(('log', msg))

    def flush(self):
        pass

class HiddenPagesApp:

    def __init__(self, root):
        self.root = root
        self.root.title('Hidden Page Finder')
        self.root.geometry('820x640')
        self.root.minsize(700, 500)
        self.log_queue = queue.Queue()
        self.worker_thread = None
        self.report_path = None
        self._build_widgets()
        self.root.after(100, self._poll_queue)

    def _build_widgets(self):
        pad = {'padx': 8, 'pady': 6}
        top = ttk.Frame(self.root)
        top.pack(fill='x', **pad)
        ttk.Label(top, text='Target domain:').grid(row=0, column=0, sticky='w')
        self.target_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.target_var, width=40).grid(row=0, column=1, sticky='we', padx=(4, 12))
        self.run_button = ttk.Button(top, text='Run Audit', command=self._on_run)
        self.run_button.grid(row=0, column=2, padx=4)
        top.columnconfigure(1, weight=1)
        opts = ttk.LabelFrame(self.root, text='Options')
        opts.pack(fill='x', **pad)
        self.no_dictionary = tk.BooleanVar()
        self.no_wayback = tk.BooleanVar()
        self.no_crawl = tk.BooleanVar()
        self.ignore_robots = tk.BooleanVar()
        ttk.Checkbutton(opts, text='Skip dictionary scan', variable=self.no_dictionary).grid(row=0, column=0, sticky='w', padx=6, pady=4)
        ttk.Checkbutton(opts, text='Skip Wayback Machine lookup', variable=self.no_wayback).grid(row=0, column=1, sticky='w', padx=6, pady=4)
        ttk.Checkbutton(opts, text='Skip navigation crawl', variable=self.no_crawl).grid(row=1, column=0, sticky='w', padx=6, pady=4)
        ttk.Checkbutton(opts, text='Ignore robots.txt during scan (only for sites you own)', variable=self.ignore_robots).grid(row=1, column=1, sticky='w', padx=6, pady=4)
        ttk.Label(opts, text='Delay between requests (sec):').grid(row=2, column=0, sticky='w', padx=6, pady=4)
        self.delay_var = tk.DoubleVar(value=0.5)
        ttk.Spinbox(opts, from_=0.0, to=5.0, increment=0.1, textvariable=self.delay_var, width=8).grid(row=2, column=1, sticky='w', padx=6, pady=4)
        out_frame = ttk.Frame(self.root)
        out_frame.pack(fill='x', **pad)
        ttk.Label(out_frame, text='Report file:').pack(side='left')
        self.output_var = tk.StringVar(value='hidden_pages_report.csv')
        ttk.Entry(out_frame, textvariable=self.output_var).pack(side='left', fill='x', expand=True, padx=6)
        ttk.Button(out_frame, text='Browse...', command=self._browse_output).pack(side='left')

        wl_frame = ttk.Frame(self.root)
        wl_frame.pack(fill='x', **pad)
        ttk.Label(wl_frame, text='Wordlist (optional):').pack(side='left')
        self.wordlist_var = tk.StringVar(value='')
        ttk.Entry(wl_frame, textvariable=self.wordlist_var).pack(side='left', fill='x', expand=True, padx=6)
        ttk.Button(wl_frame, text='Browse...', command=self._browse_wordlist).pack(side='left')
        ttk.Button(wl_frame, text='Clear', command=lambda: self.wordlist_var.set('')).pack(side='left', padx=(4, 0))
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill='x', padx=8, pady=(0, 6))
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, **pad)
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text='Log')
        self.log_text = tk.Text(log_frame, wrap='word', state='disabled', bg='#111', fg='#0f0')
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scroll.pack(side='right', fill='y')
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text='Hidden Pages')
        columns = ('url', 'source', 'status', 'linked')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings')
        for (col, label, width) in [('url', 'URL', 400), ('source', 'Source', 150), ('status', 'Status', 80), ('linked', 'Linked?', 80)]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor='w')
        tree_scroll = ttk.Scrollbar(results_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')
        bottom = ttk.Frame(self.root)
        bottom.pack(fill='x', **pad)
        self.summary_var = tk.StringVar(value='Ready.')
        ttk.Label(bottom, textvariable=self.summary_var).pack(side='left')
        self.open_report_btn = ttk.Button(bottom, text='Open Report Folder', command=self._open_report_folder, state='disabled')
        self.open_report_btn.pack(side='right')

    def _browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv'), ('JSON', '*.json')], initialfile='hidden_pages_report.csv')
        if path:
            self.output_var.set(path)

    def _browse_wordlist(self):
        path = filedialog.askopenfilename(filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if path:
            self.wordlist_var.set(path)

    def _open_report_folder(self):
        if self.report_path:
            folder = os.path.dirname(os.path.abspath(self.report_path))
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')

    def _on_run(self):
        target = self.target_var.get().strip()
        if not target:
            messagebox.showwarning('Missing target', 'Enter a domain to audit first.')
            return
        self.run_button.configure(state='disabled')
        self.open_report_btn.configure(state='disabled')
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.summary_var.set('Running...')
        self.progress.start(12)
        args = {'target': target, 'output': self.output_var.get().strip() or 'hidden_pages_report.csv', 'delay': self.delay_var.get(), 'wordlist': self.wordlist_var.get().strip() or None, 'no_dictionary': self.no_dictionary.get(), 'no_wayback': self.no_wayback.get(), 'no_crawl': self.no_crawl.get(), 'ignore_robots': self.ignore_robots.get()}
        self.worker_thread = threading.Thread(target=self._worker, args=(args,), daemon=True)
        self.worker_thread.start()

    def _worker(self, args):
        old_stdout = sys.stdout
        sys.stdout = QueueWriter(self.log_queue)
        try:
            wordlist = None
            if args.get('wordlist'):
                with open(args['wordlist']) as f:
                    wordlist = [line.strip() for line in f if line.strip()]
                print(f"Loaded {len(wordlist)} entries from custom wordlist: {args['wordlist']}")
            (discovery, report_path) = run_audit(args['target'], output=args['output'], delay=args['delay'], wordlist=wordlist, no_dictionary=args['no_dictionary'], no_wayback=args['no_wayback'], no_crawl=args['no_crawl'], ignore_robots=args['ignore_robots'])
            self.log_queue.put(('done', {'discovery': discovery, 'report_path': report_path}))
        except Exception as e:
            self.log_queue.put(('error', str(e)))
        finally:
            sys.stdout = old_stdout

    def _poll_queue(self):
        try:
            while True:
                (kind, payload) = self.log_queue.get_nowait()
                if kind == 'log':
                    self.log_text.configure(state='normal')
                    self.log_text.insert('end', payload)
                    self.log_text.see('end')
                    self.log_text.configure(state='disabled')
                elif kind == 'done':
                    self._on_done(payload)
                elif kind == 'error':
                    self._on_error(payload)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _on_done(self, payload):
        self.progress.stop()
        self.run_button.configure(state='normal')
        discovery = payload['discovery']
        self.report_path = payload['report_path']
        self.open_report_btn.configure(state='normal')
        findings = sorted(discovery.findings.values(), key=lambda f: f.url)
        hidden_count = 0
        for f in findings:
            if not f.linked:
                hidden_count += 1
                self.tree.insert('', 'end', values=(f.url, f.source, f.status, 'No'))
        self.summary_var.set(f'Done. {len(findings)} page(s) discovered, {hidden_count} hidden. Report: {self.report_path}')

    def _on_error(self, message):
        self.progress.stop()
        self.run_button.configure(state='normal')
        self.summary_var.set('Error - see log.')
        messagebox.showerror('Audit failed', message)

def gui_main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
    except Exception:
        pass
    HiddenPagesApp(root)
    root.mainloop()
if __name__ == '__main__':
    if len(sys.argv) > 1:
        cli_main(sys.argv[1:])
    else:
        gui_main()
