# Hidden Page Finder

A tool for auditing a website **you own or are authorized to test** for
hidden or orphaned pages — pages that exist but aren't linked from normal
site navigation.

It combines passive discovery methods with a light, rate-limited scan:

- **robots.txt** — reads `Disallow` rules (often the biggest tell for
  hidden admin panels, staging areas, etc.) and any `Sitemap:` references.
- **sitemap.xml** — parses sitemaps (including sitemap indexes) for listed
  pages.
- **Wayback Machine** — queries the Internet Archive's CDX API for URLs
  that have ever been archived for the domain.
- **Dictionary scan** — checks a curated list of ~60 common paths (admin
  panels, backups, `.git`, `.env`, config files, etc.) with a delay
  between requests.
- **Navigation crawl** — crawls the homepage and its linked pages to see
  what's normally reachable, then flags anything discovered above that
  *isn't* reachable that way as "hidden."

Everything is written to a single file, `hidden_page_finder.py`, which
works as both a desktop GUI and a command-line tool.

## Scope and ethics

This tool is meant for auditing sites you own or have explicit permission
to test. By default, the dictionary scan skips any path disallowed by
`robots.txt` — pass `--ignore-robots` (CLI) or check the equivalent box
(GUI) to override that, which only makes sense on your own property.
Requests are rate-limited and sent with a descriptive User-Agent string.

## Requirements

- Python 3.9+
- The `requests` package:

  ```
  pip install requests
  ```

Tkinter (used for the GUI) ships with Python on Windows and macOS by
default. On Linux you may need `sudo apt install python3-tk`.

## Running the GUI

Run the script with no arguments:

```
python hidden_page_finder.py
```

This opens a window where you can:

- Enter the target domain
- Toggle which discovery steps run (dictionary scan, Wayback lookup,
  robots.txt handling, navigation crawl)
- Set the delay between dictionary-scan requests
- Choose where the report is saved (CSV or JSON)
- Watch a live log while the audit runs
- Browse results in a table, filtered to pages not linked from normal
  navigation
- Jump to the report's folder when it's done

You can also just double-click `hidden_page_finder.py` in File Explorer
if `.py` files are associated with Python on your machine.

## Running from the command line

Pass a domain as an argument to run headless instead:

```
python hidden_page_finder.py example.com
```

Options:

| Flag | Description |
|---|---|
| `--output PATH` | Report file path (`.csv` or `.json`). Default: `hidden_pages_report.csv` |
| `--delay SECONDS` | Delay between dictionary-scan requests. Default: `0.5` |
| `--timeout SECONDS` | Request timeout. Default: `10.0` |
| `--wordlist PATH` | Custom wordlist file (one path per line) instead of the built-in list |
| `--no-dictionary` | Skip the dictionary scan |
| `--no-wayback` | Skip the Wayback Machine lookup |
| `--no-crawl` | Skip crawling the homepage for linked pages |
| `--ignore-robots` | Also actively fetch paths disallowed by robots.txt |

Example:

```
python hidden_page_finder.py example.com --output report.json --delay 1
```

## Reading the report

The report lists every discovered URL with:

- **source** — where it was found (`robots.txt`, `sitemap.xml`, `wayback`,
  `dictionary-scan`, or a combination)
- **status** — the HTTP status code observed
- **linked_from_navigation** — `True` if the page was reachable by
  crawling the homepage; `False` means it's "hidden"

## Building a standalone .exe (Windows)

```
pip install pyinstaller
pyinstaller --onefile --windowed --name HiddenPageFinder hidden_page_finder.py
```

The `.exe` will be in the new `dist` folder. `--windowed` hides the
console window for GUI use; drop it if you also want to use the CLI mode
from the built executable, since `--windowed` suppresses printed output.

First launch may trigger a Windows SmartScreen warning since the exe is
unsigned — choose "More info" → "Run anyway."
