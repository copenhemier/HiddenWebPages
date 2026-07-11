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

DEFAULT_WORDLIST = [
    '.bash_history', '.bashrc', '.cache', '.config', '.cvs', '.cvsignore', '.forward', '.git/HEAD', '.history', '.hta', '.htaccess', '.htpasswd',
    '.listing', '.listings', '.mysql_history', '.passwd', '.perf', '.profile', '.rhosts', '.sh_history', '.ssh', '.subversion', '.svn', '.svn/entries',
    '.swf', '.web', '@', '_', '_adm', '_admin', '_ajax', '_archive', '_assets', '_backup', '_baks', '_borders',
    '_cache', '_catalogs', '_code', '_common', '_conf', '_config', '_css', '_data', '_database', '_db_backups', '_derived', '_dev',
    '_dummy', '_files', '_flash', '_fpclass', '_images', '_img', '_inc', '_include', '_includes', '_install', '_js', '_layouts',
    '_lib', '_media', '_mem_bin', '_mm', '_mmserverscripts', '_mygallery', '_net', '_notes', '_old', '_overlay', '_pages', '_private',
    '_reports', '_res', '_resources', '_scriptlibrary', '_scripts', '_source', '_src', '_stats', '_styles', '_swf', '_temp', '_tempalbums',
    '_template', '_templates', '_test', '_themes', '_tmp', '_tmpfileop', '_vti_aut', '_vti_bin', '_vti_bin/_vti_adm/admin.dll', '_vti_bin/_vti_aut/author.dll', '_vti_bin/shtml.dll', '_vti_cnf',
    '_vti_inf', '_vti_log', '_vti_map', '_vti_pvt', '_vti_rpc', '_vti_script', '_vti_txt', '_www', '~adm', '~admin', '~administrator', '~amanda',
    '~apache', '~bin', '~ftp', '~guest', '~http', '~httpd', '~log', '~logs', '~lp', '~mail', '~nobody', '~operator',
    '~root', '~sys', '~sysadm', '~sysadmin', '~test', '~tmp', '~user', '~webmaster', '~www', '0', '00', '01',
    '02', '03', '04', '05', '06', '07', '08', '09', '1', '10', '100', '1000',
    '1001', '101', '102', '103', '11', '12', '123', '13', '14', '15', '1990', '1991',
    '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '1x1', '2', '20', '200',
    '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011',
    '2012', '2013', '2014', '21', '22', '2257', '23', '24', '25', '2g', '3', '30',
    '300', '32', '3g', '3rdparty', '4', '400', '401', '403', '404', '42', '5', '50',
    '500', '51', '6', '64', '7', '7z', '8', '9', '96', 'a', 'A', 'aa',
    'aaa', 'abc', 'abc123', 'abcd', 'abcd1234', 'about', 'About', 'about_us', 'aboutus', 'about-us', 'AboutUs', 'abstract',
    'abuse', 'ac', 'academic', 'academics', 'acatalog', 'acc', 'access', 'access.1', 'access_db', 'access_log', 'access_log.1', 'accessgranted',
    'accessibility', 'access-log', 'access-log.1', 'accessories', 'accommodation', 'account', 'account_edit', 'account_history', 'accountants', 'accounting', 'accounts', 'accountsettings',
    'acct_login', 'achitecture', 'acp', 'act', 'action', 'actions', 'activate', 'active', 'activeCollab', 'activex', 'activities', 'activity',
    'ad', 'ad_js', 'adaptive', 'adclick', 'add', 'add_cart', 'addfav', 'addnews', 'addons', 'addpost', 'addreply', 'address',
    'address_book', 'addressbook', 'addresses', 'addtocart', 'adlog', 'adlogger', 'adm', 'ADM', 'admin', 'Admin', 'ADMIN', 'admin.cgi',
    'admin.php', 'admin.pl', 'admin_', 'admin_area', 'admin_banner', 'admin_c', 'admin_index', 'admin_interface', 'admin_login', 'admin_logon', 'admin1', 'admin2',
    'admin3', 'admin4_account', 'admin4_colon', 'admin-admin', 'admin-console', 'admincontrol', 'admincp', 'adminhelp', 'admin-interface', 'administer', 'administr8', 'administracion',
    'administrador', 'administrat', 'administratie', 'administration', 'Administration', 'administrator', 'administratoraccounts', 'administrators', 'administrivia', 'adminlogin', 'adminlogon', 'adminpanel',
    'adminpro', 'admins', 'AdminService', 'adminsessions', 'adminsql', 'admintools', 'AdminTools', 'admissions', 'admon', 'ADMON', 'adobe', 'adodb',
    'ads', 'adserver', 'adsl', 'adv', 'adv_counter', 'advanced', 'advanced_search', 'advancedsearch', 'advert', 'advertise', 'advertisement', 'advertisers',
    'advertising', 'adverts', 'advice', 'adview', 'advisories', 'af', 'aff', 'affiche', 'affiliate', 'affiliate_info', 'affiliate_terms', 'affiliates',
    'affiliatewiz', 'africa', 'agb', 'agency', 'agenda', 'agent', 'agents', 'aggregator', 'AggreSpy', 'ajax', 'ajax_cron', 'akamai',
    'akeeba.backend.log', 'alarm', 'alarms', 'album', 'albums', 'alcatel', 'alert', 'alerts', 'alias', 'aliases', 'all', 'alltime',
    'all-wcprops', 'alpha', 'alt', 'alumni', 'alumni_add', 'alumni_details', 'alumni_info', 'alumni_reunions', 'alumni_update', 'am', 'amanda', 'amazon',
    'amember', 'analog', 'analyse', 'analysis', 'analytics', 'and', 'android', 'announce', 'announcement', 'announcements', 'annuaire', 'annual',
    'anon', 'anon_ftp', 'anonymous', 'ansi', 'answer', 'answers', 'antibot_image', 'antispam', 'antivirus', 'anuncios', 'any', 'aol',
    'ap', 'apac', 'apache', 'apanel', 'apc', 'apexec', 'api', 'apis', 'apl', 'apm', 'app', 'app_browser',
    'app_browsers', 'app_code', 'app_data', 'app_themes', 'appeal', 'appeals', 'append', 'appl', 'apple', 'applet', 'applets', 'appliance',
    'appliation', 'application', 'application.wadl', 'applications', 'apply', 'apps', 'AppsLocalLogin', 'AppsLogin', 'apr', 'ar', 'arbeit', 'arcade',
    'arch', 'architect', 'architecture', 'archiv', 'archive', 'Archive', 'archives', 'archivos', 'arquivos', 'array', 'arrow', 'ars',
    'art', 'article', 'articles', 'Articles', 'artikel', 'artists', 'arts', 'artwork', 'as', 'ascii', 'asdf', 'ashley',
    'asia', 'ask', 'ask_a_question', 'askapache', 'asmx', 'asp', 'aspadmin', 'aspdnsfcommon', 'aspdnsfencrypt', 'aspdnsfgateways', 'aspdnsfpatterns', 'aspnet_client',
    'asps', 'aspx', 'asset', 'assetmanage', 'assetmanagement', 'assets', 'at', 'AT-admin.cgi', 'atom', 'attach', 'attach_mod', 'attachment',
    'attachments', 'attachs', 'attic', 'au', 'auction', 'auctions', 'audio', 'audit', 'audits', 'auth', 'authentication', 'author',
    'authoring', 'authorization', 'authorized_keys', 'authors', 'authuser', 'authusers', 'auto', 'autobackup', 'autocheck', 'autodeploy', 'autodiscover', 'autologin',
    'automatic', 'automation', 'automotive', 'aux', 'av', 'avatar', 'avatars', 'aw', 'award', 'awardingbodies', 'awards', 'awl',
    'awmdata', 'awstats', 'awstats.conf', 'axis', 'axis2', 'axis2-admin', 'axis-admin', 'axs', 'az', 'b', 'B', 'b1',
    'b2b', 'b2c', 'back', 'backdoor', 'backend', 'background', 'backgrounds', 'backoffice', 'BackOffice', 'backup', 'back-up', 'backup_migrate',
    'backup2', 'backup-db', 'backups', 'bad_link', 'bak', 'bakup', 'bak-up', 'balance', 'balances', 'ban', 'bandwidth', 'bank',
    'banking', 'banks', 'banned', 'banner', 'banner_element', 'banner2', 'banneradmin', 'bannerads', 'banners', 'bar', 'base', 'Base',
    'baseball', 'bash', 'basic', 'basket', 'basketball', 'baskets', 'bass', 'bat', 'batch', 'baz', 'bb', 'bbadmin',
    'bbclone', 'bb-hist', 'bb-histlog', 'bboard', 'bbs', 'bc', 'bd', 'bdata', 'be', 'bea', 'bean', 'beans',
    'beehive', 'beheer', 'benefits', 'benutzer', 'best', 'beta', 'bfc', 'bg', 'big', 'bigadmin', 'bigip', 'bilder',
    'bill', 'billing', 'bin', 'binaries', 'binary', 'bins', 'bio', 'bios', 'bitrix', 'biz', 'bk', 'bkup',
    'bl', 'black', 'blah', 'blank', 'blb', 'block', 'blocked', 'blocks', 'blog', 'Blog', 'blog_ajax', 'blog_inlinemod',
    'blog_report', 'blog_search', 'blog_usercp', 'blogger', 'bloggers', 'blogindex', 'blogs', 'blogspot', 'blow', 'blue', 'bm', 'bmz_cache',
    'bnnr', 'bo', 'board', 'boards', 'bob', 'body', 'bofh', 'boiler', 'boilerplate', 'bonus', 'bonuses', 'book',
    'booker', 'booking', 'bookmark', 'bookmarks', 'books', 'Books', 'bookstore', 'boost_stats', 'boot', 'bot', 'bots', 'bottom',
    'bot-trap', 'boutique', 'box', 'boxes', 'br', 'brand', 'brands', 'broadband', 'brochure', 'brochures', 'broken', 'broken_link',
    'broker', 'browse', 'browser', 'Browser', 'bs', 'bsd', 'bt', 'bug', 'bugs', 'build', 'BUILD', 'builder',
    'buildr', 'bulk', 'bulksms', 'bullet', 'busca', 'buscador', 'buscar', 'business', 'Business', 'button', 'buttons', 'buy',
    'buynow', 'buyproduct', 'bypass', 'bz2', 'c', 'C', 'ca', 'cabinet', 'cache', 'cachemgr', 'cachemgr.cgi', 'caching',
    'cad', 'cadmins', 'cal', 'calc', 'calendar', 'calendar_events', 'calendar_sports', 'calendarevents', 'calendars', 'calender', 'call', 'callback',
    'callee', 'caller', 'callin', 'calling', 'callout', 'cam', 'camel', 'campaign', 'campaigns', 'can', 'canada', 'captcha',
    'car', 'carbuyaction', 'card', 'cardinal', 'cardinalauth', 'cardinalform', 'cards', 'career', 'careers', 'carp', 'carpet', 'cars',
    'cart', 'carthandler', 'carts', 'cas', 'cases', 'casestudies', 'cash', 'cat', 'catalog', 'catalog.wci', 'catalogs', 'catalogsearch',
    'catalogue', 'catalyst', 'catch', 'categoria', 'categories', 'category', 'catinfo', 'cats', 'cb', 'cc', 'ccbill', 'ccount',
    'ccp14admin', 'ccs', 'cd', 'cdrom', 'centres', 'cert', 'certenroll', 'certificate', 'certificates', 'certification', 'certified', 'certs',
    'certserver', 'certsrv', 'cf', 'cfc', 'cfcache', 'cfdocs', 'cfg', 'cfide', 'cfm', 'cfusion', 'cgi', 'cgi_bin',
    'cgibin', 'cgi-bin', 'cgi-bin/', 'cgi-bin2', 'cgi-data', 'cgi-exe', 'cgi-home', 'cgi-image', 'cgi-local', 'cgi-perl', 'cgi-pub', 'cgis',
    'cgi-script', 'cgi-shl', 'cgi-sys', 'cgi-web', 'cgi-win', 'cgiwrap', 'cgm-web', 'ch', 'chan', 'change', 'change_password', 'changed',
    'changelog', 'ChangeLog', 'changepassword', 'changepw', 'changepwd', 'changes', 'channel', 'charge', 'charges', 'chart', 'charts', 'chat',
    'chats', 'check', 'checking', 'checkout', 'checkout_iclear', 'checkoutanon', 'checkoutreview', 'checkpoint', 'checks', 'child', 'children', 'china',
    'chk', 'choosing', 'chpasswd', 'chpwd', 'chris', 'chrome', 'cinema', 'cisco', 'cisweb', 'cities', 'citrix', 'city',
    'ck', 'ckeditor', 'ckfinder', 'cl', 'claim', 'claims', 'class', 'classes', 'classic', 'classified', 'classifieds', 'classroompages',
    'cleanup', 'clear', 'clearcookies', 'clearpixel', 'click', 'clickheat', 'clickout', 'clicks', 'client', 'clientaccesspolicy', 'clientapi', 'clientes',
    'clients', 'clientscript', 'clipart', 'clips', 'clk', 'clock', 'close', 'closed', 'closing', 'club', 'cluster', 'clusters',
    'cm', 'cmd', 'cmpi_popup', 'cms', 'CMS', 'cmsadmin', 'cn', 'cnf', 'cnstats', 'cnt', 'co', 'cocoon',
    'code', 'codec', 'codecs', 'codepages', 'codes', 'coffee', 'cognos', 'coke', 'coldfusion', 'collapse', 'collection', 'college',
    'columnists', 'columns', 'com', 'com_sun_web_ui', 'com1', 'com2', 'com3', 'comics', 'comm', 'command', 'comment', 'commentary',
    'commented', 'comment-page', 'comment-page-1', 'comments', 'commerce', 'commercial', 'common', 'commoncontrols', 'commun', 'communication', 'communications', 'communicator',
    'communities', 'community', 'comp', 'compact', 'companies', 'company', 'compare', 'compare_product', 'comparison', 'comparison_list', 'compat', 'compiled',
    'complaint', 'complaints', 'compliance', 'component', 'components', 'compose', 'composer', 'compress', 'compressed', 'computer', 'computers', 'Computers',
    'computing', 'comunicator', 'con', 'concrete', 'conditions', 'conf', 'conference', 'conferences', 'config', 'config.local', 'configs', 'configuration',
    'configure', 'confirm', 'confirmed', 'conlib', 'conn', 'connect', 'connections', 'connector', 'connectors', 'console', 'constant', 'constants',
    'consulting', 'consumer', 'cont', 'contact', 'Contact', 'contact_bean', 'contact_us', 'contact-form', 'contactinfo', 'contacto', 'contacts', 'contactus',
    'contact-us', 'ContactUs', 'contao', 'contato', 'contenido', 'content', 'Content', 'contents', 'contest', 'contests', 'contract', 'contracts',
    'contrib', 'contribute', 'contributor', 'control', 'controller', 'controllers', 'controlpanel', 'controls', 'converge_local', 'converse', 'cookie', 'cookie_usage',
    'cookies', 'cool', 'copies', 'copy', 'copyright', 'copyright-policy', 'corba', 'core', 'coreg', 'corp', 'corpo', 'corporate',
    'corporation', 'corrections', 'count', 'counter', 'counters', 'country', 'counts', 'coupon', 'coupons', 'coupons1', 'course', 'courses',
    'cover', 'covers', 'cp', 'cpadmin', 'CPAN', 'cpanel', 'cPanel', 'cpanel_file', 'cpath', 'cpp', 'cps', 'cpstyles',
    'cpw', 'cr', 'crack', 'crash', 'crashes', 'create', 'create_account', 'createaccount', 'createbutton', 'creation', 'Creatives', 'creator',
    'credit', 'creditcards', 'credits', 'crime', 'crm', 'crms', 'cron', 'cronjobs', 'crons', 'crontab', 'crontabs', 'crossdomain',
    'crossdomain.xml', 'crs', 'crtr', 'crypt', 'crypto', 'cs', 'cse', 'csproj', 'css', 'csv', 'ct', 'ctl',
    'culture', 'currency', 'current', 'custom', 'custom_log', 'customavatars', 'customcode', 'customer', 'customer_login', 'customers', 'customgroupicons', 'customize',
    'custom-log', 'cute', 'cutesoft_client', 'cv', 'cvs', 'CVS', 'CVS/Entries', 'CVS/Repository', 'CVS/Root', 'cxf', 'cy', 'CYBERDOCS',
    'CYBERDOCS25', 'CYBERDOCS31', 'cyberworld', 'cycle_image', 'cz', 'czcmdcvt', 'd', 'D', 'da', 'daemon', 'daily', 'dan',
    'dana-na', 'dark', 'dashboard', 'dat', 'data', 'database', 'database_administration', 'Database_Administration', 'databases', 'datafiles', 'datas', 'date',
    'daten', 'datenschutz', 'dating', 'dav', 'day', 'db', 'DB', 'db_connect', 'dba', 'dbadmin', 'dbase', 'dbboon',
    'dbg', 'dbi', 'dblclk', 'dbm', 'dbman', 'dbmodules', 'dbms', 'dbutil', 'dc', 'dcforum', 'dclk', 'de',
    'de_DE', 'deal', 'dealer', 'dealers', 'deals', 'debian', 'debug', 'dec', 'decl', 'declaration', 'declarations', 'decode',
    'decoder', 'decrypt', 'decrypted', 'decryption', 'def', 'default', 'Default', 'default_icon', 'default_image', 'default_logo', 'default_page', 'default_pages',
    'defaults', 'definition', 'definitions', 'del', 'delete', 'deleted', 'deleteme', 'deletion', 'delicious', 'demo', 'demo2', 'demos',
    'denied', 'deny', 'departments', 'deploy', 'deployment', 'descargas', 'design', 'designs', 'desktop', 'desktopmodules', 'desktops', 'destinations',
    'detail', 'details', 'deutsch', 'dev', 'dev2', 'dev60cgi', 'devel', 'develop', 'developement', 'developer', 'developers', 'development',
    'development.log', 'device', 'devices', 'devs', 'devtools', 'df', 'dh_', 'dh_phpmyadmin', 'di', 'diag', 'diagnostics', 'dial',
    'dialog', 'dialogs', 'diary', 'dictionary', 'diff', 'diffs', 'dig', 'digest', 'digg', 'digital', 'dir', 'dirb',
    'dirbmark', 'direct', 'directadmin', 'directions', 'directories', 'directorio', 'directory', 'dir-login', 'dir-prop-base', 'dirs', 'disabled', 'disallow',
    'disclaimer', 'disclosure', 'discootra', 'discount', 'discovery', 'discus', 'discuss', 'discussion', 'disdls', 'disk', 'dispatch', 'dispatcher',
    'display', 'display_vvcodes', 'dist', 'divider', 'django', 'dk', 'dl', 'dll', 'dm', 'dm-config', 'dmdocuments', 'dms',
    'DMSDump', 'dns', 'do', 'doc', 'docebo', 'docedit', 'dock', 'docnote', 'docroot', 'docs', 'docs41', 'docs51',
    'document', 'document_library', 'documentation', 'documents', 'Documents and Settings', 'doinfo', 'doit', 'dokuwiki', 'dologin', 'domain', 'domains', 'donate',
    'donations', 'done', 'dot', 'double', 'doubleclick', 'down', 'download', 'Download', 'download_private', 'downloader', 'downloads', 'Downloads',
    'downsys', 'draft', 'drafts', 'dragon', 'draver', 'driver', 'drivers', 'drop', 'dropped', 'drupal', 'ds', 'dummy',
    'dump', 'dumpenv', 'dumps', 'dumpuser', 'dvd', 'dwr', 'dyn', 'dynamic', 'dyop_addtocart', 'dyop_delete', 'dyop_quan', 'e',
    'E', 'e107_admin', 'e107_files', 'e107_handlers', 'e2fs', 'ear', 'easy', 'ebay', 'eblast', 'ebook', 'ebooks', 'ebriefs',
    'ec', 'ecard', 'ecards', 'echannel', 'ecommerce', 'ecrire', 'edge', 'edgy', 'edit', 'edit_link', 'edit_profile', 'editaddress',
    'editor', 'editorial', 'editorials', 'editors', 'editpost', 'edits', 'edp', 'edu', 'education', 'Education', 'ee', 'effort',
    'efforts', 'egress', 'ehdaa', 'ejb', 'el', 'electronics', 'element', 'elements', 'elmar', 'em', 'email', 'e-mail',
    'email-addresses', 'emailafriend', 'email-a-friend', 'emailer', 'emailhandler', 'emailing', 'emailproduct', 'emails', 'emailsignup', 'emailtemplates', 'embed', 'embedd',
    'embedded', 'emea', 'emergency', 'emoticons', 'employee', 'employees', 'employers', 'employment', 'empty', 'emu', 'emulator', 'en',
    'en_us', 'en_US', 'enable-cookies', 'enc', 'encode', 'encoder', 'encrypt', 'encrypted', 'encryption', 'encyption', 'end', 'enduser',
    'endusers', 'energy', 'enews', 'eng', 'engine', 'engines', 'english', 'English', 'enterprise', 'entertainment', 'Entertainment', 'entries',
    'Entries', 'entropybanner', 'entry', 'env', 'environ', 'environment', 'ep', 'eproducts', 'equipment', 'eric', 'err', 'erraddsave',
    'errata', 'error', 'error_docs', 'error_log', 'error_message', 'error_pages', 'error404', 'errordocs', 'error-espanol', 'error-log', 'errorpage', 'errorpages',
    'errors', 'erros', 'es', 'es_ES', 'esale', 'esales', 'eshop', 'esp', 'espanol', 'established', 'estilos', 'estore',
    'e-store', 'esupport', 'et', 'etc', 'ethics', 'eu', 'europe', 'evb', 'event', 'events', 'Events', 'evil',
    'evt', 'ewebeditor', 'ews', 'ex', 'example', 'examples', 'excalibur', 'excel', 'exception_log', 'exch', 'exchange', 'exchweb',
    'exclude', 'exe', 'exec', 'executable', 'executables', 'exiar', 'exit', 'expert', 'experts', 'exploits', 'explore', 'explorer',
    'export', 'exports', 'ext', 'ext2', 'extension', 'extensions', 'extern', 'external', 'externalid', 'externalisation', 'externalization', 'extra',
    'extranet', 'Extranet', 'extras', 'ez', 'ezshopper', 'ezsqliteadmin', 'f', 'F', 'fa', 'fabric', 'face', 'facebook',
    'faces', 'facts', 'faculty', 'fail', 'failed', 'failure', 'fake', 'family', 'fancybox', 'faq', 'FAQ', 'faqs',
    'fashion', 'favicon.ico', 'favorite', 'favorites', 'fb', 'fbook', 'fc', 'fcategory', 'fcgi', 'fcgi-bin', 'fck', 'fckeditor',
    'FCKeditor', 'fdcp', 'feature', 'featured', 'features', 'fedora', 'feed', 'feedback', 'feedback_js', 'feeds', 'felix', 'fetch',
    'fi', 'field', 'fields', 'file', 'fileadmin', 'filelist', 'filemanager', 'files', 'filesystem', 'fileupload', 'fileuploads', 'filez',
    'film', 'films', 'filter', 'finance', 'financial', 'find', 'finger', 'finishorder', 'firefox', 'firewall', 'firewalls', 'firmconnect',
    'firms', 'firmware', 'first', 'fixed', 'fk', 'fla', 'flag', 'flags', 'flash', 'flash-intro', 'flex', 'flights',
    'flow', 'flowplayer', 'flows', 'flv', 'flvideo', 'flyspray', 'fm', 'fn', 'focus', 'foia', 'folder', 'folder_new',
    'folders', 'font', 'fonts', 'foo', 'food', 'football', 'footer', 'footers', 'for', 'forcedownload', 'forget', 'forgot',
    'forgot_password', 'forgotpassword', 'forgot-password', 'forgotten', 'form', 'format', 'formatting', 'formhandler', 'formmail', 'forms', 'forms1', 'formsend',
    'formslogin', 'formupdate', 'foro', 'foros', 'forrest', 'fortune', 'forum', 'forum_old', 'forum1', 'forum2', 'forumcp', 'forumdata',
    'forumdisplay', 'forums', 'forward', 'foto', 'fotos', 'foundation', 'fpdb', 'fpdf', 'fr', 'fr_FR', 'frame', 'frames',
    'frameset', 'framework', 'francais', 'france', 'free', 'freebsd', 'freeware', 'french', 'friend', 'friends', 'frm_attach', 'frob',
    'from', 'front', 'frontend', 'frontpage', 'fs', 'fsck', 'ftp', 'fuck', 'fuckoff', 'fuckyou', 'full', 'fun',
    'func', 'funcs', 'function', 'function.require', 'functionlude', 'functions', 'fund', 'funding', 'funds', 'furl', 'fusion', 'future',
    'fw', 'fwlink', 'fx', 'g', 'G', 'ga', 'gadget', 'gadgets', 'gaestebuch', 'galeria', 'galerie', 'galleries',
    'gallery', 'gallery2', 'game', 'gamercard', 'games', 'Games', 'gaming', 'ganglia', 'garbage', 'gate', 'gateway', 'gb',
    'gbook', 'gccallback', 'gdform', 'geeklog', 'gen', 'general', 'generateditems', 'generator', 'generic', 'gentoo', 'geo', 'geoip',
    'german', 'geronimo', 'gest', 'gestion', 'gestione', 'get', 'get_file', 'getaccess', 'getconfig', 'getfile', 'get-file', 'getFile.cfm',
    'getjobid', 'getout', 'gettxt', 'gfen', 'gfx', 'gg', 'gid', 'gif', 'gifs', 'gift', 'giftcert', 'giftoptions',
    'giftreg_manage', 'giftregs', 'gifts', 'git', 'gitweb', 'gl', 'glance_config', 'glimpse', 'global', 'Global', 'global.asa', 'global.asax',
    'globalnav', 'globals', 'globes_admin', 'glossary', 'go', 'goaway', 'gold', 'golf', 'gone', 'goods', 'goods_script', 'google',
    'google_sitemap', 'googlebot', 'goto', 'government', 'gp', 'gpapp', 'gpl', 'gprs', 'gps', 'gr', 'gracias', 'grafik',
    'grant', 'granted', 'grants', 'graph', 'graphics', 'Graphics', 'green', 'greybox', 'grid', 'group', 'group_inlinemod', 'groupcp',
    'groups', 'groupware', 'gs', 'gsm', 'guess', 'guest', 'guestbook', 'guests', 'guest-tracking', 'gui', 'guide', 'guidelines',
    'guides', 'gump', 'gv_faq', 'gv_redeem', 'gv_send', 'gwt', 'gz', 'h', 'H', 'hack', 'hacker', 'hacking',
    'hackme', 'hadoop', 'handle', 'handler', 'handlers', 'handles', 'happen', 'happening', 'hard', 'hardcore', 'hardware', 'harm',
    'harming', 'harmony', 'head', 'header', 'header_logo', 'headers', 'headlines', 'health', 'Health', 'healthcare', 'hello', 'helloworld',
    'help', 'Help', 'help_answer', 'helpdesk', 'helper', 'helpers', 'hi', 'hidden', 'hide', 'high', 'highslide', 'hilfe',
    'hipaa', 'hire', 'history', 'hit', 'hitcount', 'hits', 'hold', 'hole', 'holiday', 'holidays', 'home', 'Home',
    'homepage', 'homes', 'homework', 'honda', 'hooks', 'hop', 'horde', 'host', 'hosted', 'hosting', 'host-manager', 'hosts',
    'hotel', 'hotels', 'hour', 'hourly', 'house', 'how', 'howto', 'hp', 'hpwebjetadmin', 'hr', 'ht', 'hta',
    'htbin', 'htdig', 'htdoc', 'htdocs', 'htm', 'html', 'HTML', 'htmlarea', 'htmls', 'htpasswd', 'http', 'httpd',
    'httpdocs', 'httpmodules', 'https', 'httpuser', 'hu', 'human', 'humans', 'humor', 'hyper', 'i', 'I', 'ia',
    'ibm', 'icat', 'ico', 'icon', 'icons', 'icq', 'id', 'id_rsa', 'id_rsa.pub', 'idbc', 'idea', 'ideas',
    'identity', 'idp', 'ids', 'ie', 'if', 'iframe', 'iframes', 'ig', 'ignore', 'ignoring', 'iis', 'iisadmin',
    'iisadmpwd', 'iissamples', 'im', 'image', 'Image', 'imagefolio', 'imagegallery', 'imagenes', 'imagens', 'images', 'Images', 'images01',
    'images1', 'images2', 'images3', 'imanager', 'img', 'img2', 'imgs', 'immagini', 'imp', 'import', 'important', 'imports',
    'impressum', 'in', 'inbound', 'inbox', 'inc', 'incl', 'include', 'includes', 'incoming', 'incs', 'incubator', 'index',
    'Index', 'index.htm', 'index.html', 'index.php', 'index_01', 'index_1', 'index_2', 'index_adm', 'index_admin', 'index_files', 'index_var_de', 'index1',
    'index2', 'index3', 'indexes', 'industries', 'industry', 'indy_admin', 'Indy_admin', 'inetpub', 'inetsrv', 'inf', 'info', 'info.php',
    'information', 'informer', 'infos', 'infraction', 'ingres', 'ingress', 'ini', 'init', 'injection', 'inline', 'inlinemod', 'input',
    'inquire', 'inquiries', 'inquiry', 'insert', 'install', 'install.mysql', 'install.pgsql', 'INSTALL_admin', 'installation', 'installer', 'installwordpress', 'install-xaff',
    'install-xaom', 'install-xbench', 'install-xfcomp', 'install-xoffers', 'install-xpconf', 'install-xrma', 'install-xsurvey', 'instance', 'instructions', 'insurance', 'int', 'intel',
    'intelligence', 'inter', 'interactive', 'interface', 'interim', 'intermediate', 'intern', 'internal', 'international', 'internet', 'Internet', 'interview',
    'interviews', 'intl', 'intra', 'intracorp', 'intranet', 'intro', 'introduction', 'inventory', 'investors', 'invitation', 'invite', 'invoice',
    'invoices', 'ioncube', 'ip', 'ipc', 'ipdata', 'iphone', 'ipn', 'ipod', 'ipp', 'ips', 'ips_kernel', 'ir',
    'iraq', 'irc', 'irc-macadmin', 'is', 'isapi', 'is-bin', 'iso', 'isp', 'issue', 'issues', 'it', 'it_IT',
    'ita', 'item', 'items', 'iw', 'j', 'J', 'j2ee', 'j2me', 'ja', 'ja_JP', 'jacob', 'jakarta',
    'japan', 'jar', 'java', 'Java', 'javac', 'javadoc', 'java-plugin', 'javascript', 'javascripts', 'java-sys', 'javax', 'jboss',
    'jbossas', 'jbossws', 'jdbc', 'jdk', 'jennifer', 'jessica', 'jexr', 'jhtml', 'jigsaw', 'jira', 'jj', 'jmx-console',
    'JMXSoapAdapter', 'job', 'jobs', 'joe', 'john', 'join', 'joinrequests', 'joomla', 'journal', 'journals', 'jp', 'jpa',
    'jpegimage', 'jpg', 'jquery', 'jre', 'jrun', 'js', 'jscript', 'jscripts', 'jsession', 'jsf', 'jsFiles', 'js-lib',
    'json', 'json-api', 'jsp', 'jsp2', 'jsp-examples', 'jsps', 'jsr', 'jsso', 'jsx', 'jump', 'juniper', 'junk',
    'jvm', 'k', 'katalog', 'kb', 'kb_results', 'kboard', 'kcaptcha', 'keep', 'kept', 'kernel', 'key', 'keygen',
    'keys', 'keyword', 'keywords', 'kids', 'kill', 'kiosk', 'known_hosts', 'ko', 'ko_KR', 'kontakt', 'konto-eroeffnen', 'kr',
    'kunden', 'l', 'L', 'la', 'lab', 'labels', 'labs', 'landing', 'landingpages', 'landwind', 'lang', 'lang-en',
    'lang-fr', 'langs', 'language', 'languages', 'laptops', 'large', 'lastnews', 'lastpost', 'lat_account', 'lat_driver', 'lat_getlinking', 'lat_signin',
    'lat_signout', 'lat_signup', 'latest', 'launch', 'launcher', 'launchpage', 'law', 'layout', 'layouts', 'ldap', 'leader', 'leaders',
    'leads', 'learn', 'learners', 'learning', 'left', 'legacy', 'legal', 'Legal', 'legal-notice', 'legislation', 'lenya', 'lessons',
    'letters', 'level', 'lg', 'lgpl', 'lib', 'librairies', 'libraries', 'library', 'libs', 'lic', 'licence', 'license',
    'LICENSE', 'license_afl', 'licenses', 'licensing', 'life', 'lifestyle', 'lightbox', 'limit', 'line', 'link', 'linkex', 'linkmachine',
    'links', 'Links', 'links_submit', 'linktous', 'link-to-us', 'linux', 'Linux', 'lisence', 'lisense', 'list', 'list_users', 'listadmin',
    'list-create', 'list-edit', 'listinfo', 'listing', 'listings', 'lists', 'list-search', 'listusers', 'list-users', 'listview', 'list-view', 'live',
    'livechat', 'livehelp', 'livesupport', 'livezilla', 'lo', 'load', 'loader', 'loading', 'loc', 'local', 'locale', 'localstart',
    'location', 'locations', 'locator', 'lock', 'locked', 'lockout', 'lofiversion', 'log', 'Log', 'log4j', 'log4net', 'logfile',
    'logfiles', 'LogFiles', 'logfileview', 'logger', 'logging', 'login', 'Login', 'login_db', 'login_sendpass', 'login1', 'loginadmin', 'loginflat',
    'login-redirect', 'logins', 'login-us', 'logo', 'logo_sysadmin', 'logoff', 'logon', 'logos', 'logout', 'logs', 'Logs', 'logview',
    'loja', 'lost', 'lost+found', 'lostpassword', 'Lotus_Domino_Admin', 'love', 'low', 'lp', 'lpt1', 'lpt2', 'ls', 'lst',
    'lt', 'lucene', 'lunch_menu', 'lv', 'm', 'M', 'm_images', 'm1', 'm6', 'm6_edit_item', 'm6_invoice', 'm6_pay',
    'm7', 'ma', 'mac', 'macadmin', 'macromedia', 'maestro', 'magazin', 'magazine', 'magazines', 'magento', 'magic', 'magnifier_xml',
    'magpierss', 'mail', 'mail_link', 'mail_password', 'mailbox', 'mailer', 'mailing', 'mailinglist', 'mailings', 'maillist', 'mailman', 'mails',
    'mailtemplates', 'mailto', 'main', 'Main', 'main.mdb', 'Main_Page', 'mainfile', 'maint', 'maintainers', 'mainten', 'maintenance', 'makefile',
    'Makefile', 'mal', 'mall', 'mambo', 'mambots', 'man', 'mana', 'manage', 'managed', 'management', 'manager', 'manifest',
    'manifest.mf', 'MANIFEST.MF', 'mantis', 'manual', 'manuallogin', 'manuals', 'manufacturer', 'manufacturers', 'map', 'maps', 'mark', 'market',
    'marketing', 'marketplace', 'markets', 'master', 'master.passwd', 'masterpages', 'masters', 'masthead', 'match', 'matches', 'math', 'matrix',
    'matt', 'maven', 'mb', 'mbo', 'mbox', 'mc', 'mchat', 'mcp', 'mdb', 'mdb-database', 'me', 'media',
    'Media', 'media_center', 'mediakit', 'mediaplayer', 'medias', 'mediawiki', 'medium', 'meetings', 'mein-konto', 'mein-merkzettel', 'mem', 'member',
    'member2', 'memberlist', 'members', 'Members', 'membership', 'membre', 'membres', 'memcached', 'memcp', 'memlogin', 'memo', 'memory',
    'menu', 'menus', 'Menus', 'merchant', 'merchant2', 'message', 'messageboard', 'messages', 'messaging', 'meta', 'meta_login', 'meta_tags',
    'metabase', 'metadata', 'metaframe', 'meta-inf', 'META-INF', 'metatags', 'mgr', 'michael', 'microsoft', 'midi', 'migrate', 'migrated',
    'migration', 'military', 'min', 'mina', 'mine', 'mini', 'mini_cal', 'minicart', 'minimum', 'mint', 'minute', 'mirror',
    'mirrors', 'misc', 'Misc', 'miscellaneous', 'missing', 'mission', 'mix', 'mk', 'mkstats', 'ml', 'mlist', 'mm',
    'mm5', 'mms', 'mmwip', 'mo', 'mobi', 'mobil', 'mobile', 'mock', 'mod', 'modcp', 'mode', 'model',
    'models', 'modelsearch', 'modem', 'moderation', 'moderator', 'modify', 'modlogan', 'mods', 'module', 'modules', 'modulos', 'mojo',
    'money', 'monitor', 'monitoring', 'monitors', 'month', 'monthly', 'moodle', 'more', 'motd', 'moto1', 'moto-news', 'mount',
    'move', 'moved', 'movie', 'movies', 'moving.page', 'mozilla', 'mp', 'mp3', 'mp3s', 'mqseries', 'mrtg', 'ms',
    'msadc', 'msadm', 'msft', 'msg', 'msie', 'msn', 'msoffice', 'mspace', 'msql', 'mssql', 'ms-sql', 'mstpre',
    'mt', 'mta', 'mt-bin', 'mt-search', 'mt-static', 'multi', 'multimedia', 'music', 'Music', 'mx', 'my', 'myaccount',
    'my-account', 'myadmin', 'myblog', 'mycalendar', 'mycgi', 'my-components', 'myfaces', 'my-gift-registry', 'myhomework', 'myicons', 'mypage', 'myphpnuke',
    'myspace', 'mysql', 'my-sql', 'mysqld', 'mysqldumper', 'mysqlmanager', 'mytag_js', 'mytp', 'my-wishlist', 'n', 'N', 'nachrichten',
    'nagios', 'name', 'names', 'national', 'nav', 'navigation', 'navsiteadmin', 'navSiteAdmin', 'nc', 'ne', 'net', 'netbsd',
    'netcat', 'nethome', 'nets', 'netscape', 'netstat', 'netstorage', 'network', 'networking', 'new', 'newadmin', 'newattachment', 'newposts',
    'newreply', 'news', 'News', 'news_insert', 'newsadmin', 'newsite', 'newsletter', 'newsletters', 'newsline', 'newsroom', 'newssys', 'newstarter',
    'newthread', 'newticket', 'next', 'nfs', 'nice', 'nieuws', 'ningbar', 'nk9', 'nl', 'no', 'nobody', 'node',
    'noindex', 'no-index', 'nokia', 'none', 'note', 'notes', 'notfound', 'noticias', 'notification', 'notifications', 'notified', 'notifier',
    'notify', 'novell', 'nr', 'ns', 'nsf', 'ntopic', 'nude', 'nuke', 'nul', 'null', 'number', 'nxfeed',
    'nz', 'o', 'O', 'OA', 'OA_HTML', 'oa_servlets', 'OAErrorDetailPage', 'OasDefault', 'oauth', 'obdc', 'obj', 'object',
    'objects', 'obsolete', 'obsoleted', 'odbc', 'ode', 'oem', 'of', 'ofbiz', 'off', 'offer', 'offerdetail', 'offers',
    'office', 'Office', 'offices', 'offline', 'ogl', 'old', 'old_site', 'oldie', 'oldsite', 'old-site', 'omited', 'on',
    'onbound', 'online', 'onsite', 'op', 'open', 'open-account', 'openads', 'openapp', 'openbsd', 'opencart', 'opendir', 'openejb',
    'openfile', 'openjpa', 'opensearch', 'opensource', 'openvpnadmin', 'openx', 'opera', 'operations', 'operator', 'opinion', 'opinions', 'opml',
    'opros', 'opt', 'option', 'options', 'ora', 'oracle', 'oradata', 'order', 'order_history', 'order_status', 'order-detail', 'orderdownloads',
    'ordered', 'orderfinished', 'order-follow', 'order-history', 'order-opc', 'order-return', 'orders', 'order-slip', 'orderstatus', 'ordertotal', 'org', 'organisation',
    'organisations', 'organizations', 'orig', 'original', 'os', 'osc', 'oscommerce', 'other', 'others', 'otrs', 'out', 'outcome',
    'outgoing', 'outils', 'outline', 'output', 'outreach', 'oversikt', 'overview', 'owa', 'owl', 'owners', 'ows', 'ows-bin',
    'p', 'P', 'p2p', 'p7pm', 'pa', 'pack', 'package', 'packaged', 'packages', 'packaging', 'packed', 'pad',
    'page', 'page_1', 'page_2', 'page_sample1', 'page1', 'page2', 'pageid', 'pagenotfound', 'page-not-found', 'pager', 'pages', 'Pages',
    'pagination', 'paid', 'paiement', 'pam', 'panel', 'panelc', 'paper', 'papers', 'parse', 'part', 'partenaires', 'partner',
    'partners', 'parts', 'party', 'pass', 'passes', 'passive', 'passport', 'passw', 'passwd', 'passwor', 'password', 'passwords',
    'past', 'patch', 'patches', 'patents', 'path', 'pay', 'payment', 'payment_gateway', 'payments', 'paypal', 'paypal_notify', 'paypalcancel',
    'paypalok', 'pbc_download', 'pbcs', 'pbcsad', 'pbcsi', 'pbo', 'pc', 'pci', 'pconf', 'pd', 'pda', 'pdf',
    'PDF', 'pdf-invoice', 'pdf-order-slip', 'pdfs', 'pear', 'peek', 'peel', 'pem', 'pending', 'people', 'People', 'perf',
    'performance', 'perl', 'perl5', 'person', 'personal', 'personals', 'pfx', 'pg', 'pgadmin', 'pgp', 'pgsql', 'phf',
    'phishing', 'phone', 'phones', 'phorum', 'photo', 'photodetails', 'photogallery', 'photography', 'photos', 'php', 'PHP', 'php.ini',
    'php_uploads', 'php168', 'php3', 'phpadmin', 'phpads', 'phpadsnew', 'phpbb', 'phpBB', 'phpbb2', 'phpBB2', 'phpbb3', 'phpBB3',
    'php-bin', 'php-cgi', 'phpEventCalendar', 'phpinfo', 'phpinfo.php', 'phpinfos', 'phpldapadmin', 'phplist', 'phplive', 'phpmailer', 'phpmanual', 'phpmv2',
    'phpmyadmin', 'phpMyAdmin', 'phpmyadmin2', 'phpMyAdmin2', 'phpnuke', 'phppgadmin', 'phps', 'phpsitemapng', 'phpSQLiteAdmin', 'phpthumb', 'phtml', 'pic',
    'pics', 'picts', 'picture', 'picture_library', 'picturecomment', 'pictures', 'pii', 'ping', 'pingback', 'pipe', 'pipermail', 'piranha',
    'pivot', 'piwik', 'pix', 'pixel', 'pixelpost', 'pkg', 'pkginfo', 'pkgs', 'pl', 'placeorder', 'places', 'plain',
    'plate', 'platz_login', 'play', 'player', 'player.swf', 'players', 'playing', 'playlist', 'please', 'plenty', 'plesk-stat', 'pls',
    'plugin', 'plugins', 'plus', 'plx', 'pm', 'pma', 'PMA', 'pmwiki', 'pnadodb', 'png', 'pntables', 'pntemp',
    'poc', 'podcast', 'podcasting', 'podcasts', 'poi', 'poker', 'pol', 'policies', 'policy', 'politics', 'poll', 'pollbooth',
    'polls', 'pollvote', 'pool', 'pop', 'pop3', 'popular', 'populate', 'popup', 'popup_content', 'popup_cvv', 'popup_image', 'popup_info',
    'popup_magnifier', 'popup_poptions', 'popups', 'porn', 'port', 'portal', 'portals', 'portfolio', 'portfoliofiles', 'portlet', 'portlets', 'ports',
    'pos', 'post', 'post_thanks', 'postcard', 'postcards', 'posted', 'postgres', 'postgresql', 'posthistory', 'postinfo', 'posting', 'postings',
    'postnuke', 'postpaid', 'postreview', 'posts', 'posttocar', 'power', 'power_user', 'pp', 'ppc', 'ppcredir', 'ppt', 'pr',
    'pr0n', 'pre', 'preferences', 'preload', 'premiere', 'premium', 'prepaid', 'prepare', 'presentation', 'presentations', 'preserve', 'press',
    'Press', 'press_releases', 'presse', 'pressreleases', 'pressroom', 'prev', 'preview', 'previews', 'previous', 'price', 'pricelist', 'prices',
    'pricing', 'print', 'print_order', 'printable', 'printarticle', 'printenv', 'printer', 'printers', 'printmail', 'printpdf', 'printthread', 'printview',
    'priv', 'privacy', 'Privacy', 'privacy_policy', 'privacypolicy', 'privacy-policy', 'privat', 'private', 'private2', 'privateassets', 'privatemsg', 'prive',
    'privmsg', 'privs', 'prn', 'pro', 'probe', 'problems', 'proc', 'procedures', 'process', 'process_order', 'processform', 'procure',
    'procurement', 'prod', 'prodconf', 'prodimages', 'producers', 'product', 'product_compare', 'product_image', 'product_images', 'product_info', 'product_reviews', 'product_thumb',
    'productdetails', 'productimage', 'production', 'production.log', 'productquestion', 'products', 'Products', 'products_new', 'product-sort', 'productspecs', 'productupdates', 'produkte',
    'professor', 'profil', 'profile', 'profiles', 'profiling', 'proftpd', 'prog', 'program', 'Program Files', 'programming', 'programs', 'progress',
    'project', 'project-admins', 'projects', 'Projects', 'promo', 'promos', 'promoted', 'promotion', 'promotions', 'proof', 'proofs', 'prop',
    'prop-base', 'properties', 'property', 'props', 'prot', 'protect', 'protected', 'protection', 'proto', 'provider', 'providers', 'proxies',
    'proxy', 'prueba', 'pruebas', 'prv', 'prv_download', 'ps', 'psd', 'psp', 'psql', 'pt', 'pt_BR', 'ptopic',
    'pub', 'public', 'public_ftp', 'public_html', 'publication', 'publications', 'Publications', 'publicidad', 'publish', 'published', 'publisher', 'pubs',
    'pull', 'purchase', 'purchases', 'purchasing', 'pureadmin', 'push', 'put', 'putty', 'putty.reg', 'pw', 'pw_ajax', 'pw_api',
    'pw_app', 'pwd', 'py', 'python', 'q', 'q1', 'q2', 'q3', 'q4', 'qa', 'qinetiq', 'qotd',
    'qpid', 'qsc', 'quarterly', 'queries', 'query', 'question', 'questions', 'queue', 'queues', 'quick', 'quickstart', 'quiz',
    'quote', 'quotes', 'r', 'R', 'r57', 'radcontrols', 'radio', 'radmind', 'radmind-1', 'rail', 'rails', 'Rakefile',
    'ramon', 'random', 'rank', 'ranks', 'rar', 'rarticles', 'rate', 'ratecomment', 'rateit', 'ratepic', 'rates', 'ratethread',
    'rating', 'rating0', 'ratings', 'rb', 'rcLogin', 'rcp', 'rcs', 'RCS', 'rct', 'rd', 'rdf', 'read',
    'reader', 'readfile', 'readfolder', 'readme', 'Readme', 'README', 'real', 'realaudio', 'realestate', 'RealMedia', 'receipt', 'receipts',
    'receive', 'received', 'recent', 'recharge', 'recherche', 'recipes', 'recommend', 'recommends', 'record', 'recorded', 'recorder', 'records',
    'recoverpassword', 'recovery', 'recycle', 'recycled', 'Recycled', 'red', 'reddit', 'redesign', 'redir', 'redirect', 'redirection', 'redirector',
    'redirects', 'redis', 'ref', 'refer', 'reference', 'references', 'referer', 'referral', 'referrers', 'refuse', 'refused', 'reg',
    'reginternal', 'region', 'regional', 'register', 'registered', 'registration', 'registrations', 'registro', 'reklama', 'related', 'release', 'releases',
    'religion', 'remind', 'remind_password', 'reminder', 'remote', 'remotetracer', 'removal', 'removals', 'remove', 'removed', 'render', 'rendered',
    'reorder', 'rep', 'repl', 'replica', 'replicas', 'replicate', 'replicated', 'replication', 'replicator', 'reply', 'repo', 'report',
    'reporting', 'reports', 'reports list', 'repository', 'repost', 'reprints', 'reputation', 'req', 'reqs', 'request', 'requested', 'requests',
    'require', 'requisite', 'requisition', 'requisitions', 'res', 'research', 'Research', 'reseller', 'resellers', 'reservation', 'reservations', 'resin',
    'resin-admin', 'resize', 'resolution', 'resolve', 'resolved', 'resource', 'resources', 'Resources', 'respond', 'responder', 'rest', 'restaurants',
    'restore', 'restored', 'restricted', 'result', 'results', 'resume', 'resumes', 'retail', 'returns', 'reusablecontent', 'reverse', 'reversed',
    'revert', 'reverted', 'review', 'reviews', 'rfid', 'rhtml', 'right', 'ro', 'roadmap', 'roam', 'roaming', 'robot',
    'robotics', 'robots', 'robots.txt', 'role', 'roles', 'roller', 'room', 'root', 'Root', 'rorentity', 'rorindex', 'rortopics',
    'route', 'router', 'routes', 'rpc', 'rs', 'rsa', 'rss', 'RSS', 'rss10', 'rss2', 'rss20', 'rssarticle',
    'rssfeed', 'rsync', 'rte', 'rtf', 'ru', 'rub', 'ruby', 'rule', 'rules', 'run', 'rus', 'rwservlet',
    's', 'S', 's1', 'sa', 'safe', 'safety', 'sale', 'sales', 'salesforce', 'sam', 'samba', 'saml',
    'sample', 'samples', 'san', 'sandbox', 'sav', 'save', 'saved', 'saves', 'sb', 'sbin', 'sc', 'scan',
    'scanned', 'scans', 'scgi-bin', 'sched', 'schedule', 'scheduled', 'scheduling', 'schema', 'schemas', 'schemes', 'school', 'schools',
    'science', 'scope', 'scr', 'scratc', 'screen', 'screens', 'screenshot', 'screenshots', 'script', 'scripte', 'scriptlet', 'scriptlets',
    'scriptlibrary', 'scriptresource', 'scripts', 'Scripts', 'sd', 'sdk', 'se', 'search', 'Search', 'search_result', 'search_results', 'searchnx',
    'searchresults', 'search-results', 'searchurl', 'sec', 'seccode', 'second', 'secondary', 'secret', 'secrets', 'section', 'sections', 'secure',
    'secure_login', 'secureauth', 'secured', 'secureform', 'secureprocess', 'securimage', 'security', 'Security', 'seed', 'select', 'selectaddress', 'selected',
    'selection', 'self', 'sell', 'sem', 'seminar', 'seminars', 'send', 'send_order', 'send_pwd', 'send_to_friend', 'sendform', 'sendfriend',
    'sendmail', 'sendmessage', 'send-password', 'sendpm', 'sendthread', 'sendto', 'sendtofriend', 'sensepost', 'sensor', 'sent', 'seo', 'serial',
    'serv', 'serve', 'server', 'Server', 'server_admin_small', 'server_stats', 'ServerAdministrator', 'SERVER-INF', 'server-info', 'servers', 'server-status', 'service',
    'servicelist', 'services', 'Services', 'servicio', 'servicios', 'servlet', 'Servlet', 'servlets', 'Servlets', 'servlets-examples', 'sess', 'session',
    'sessionid', 'sessionlist', 'sessions', 'set', 'setcurrency', 'setlocale', 'setting', 'settings', 'setup', 'setvatsetting', 'sex', 'sf',
    'sg', 'sh', 'shadow', 'shaken', 'share', 'shared', 'shares', 'shell', 'shim', 'ship', 'shipped', 'shipping',
    'shipping_help', 'shippinginfo', 'shipquote', 'shit', 'shockwave', 'shop', 'shop_closed', 'shop_content', 'shopadmin', 'shopper', 'shopping', 'shopping_cart',
    'shoppingcart', 'shopping-lists', 'shops', 'shops_buyaction', 'shopstat', 'shopsys', 'shoutbox', 'show', 'show_post', 'show_thread', 'showallsites', 'showcase',
    'showcat', 'showcode', 'showenv', 'showgroups', 'showjobs', 'showkey', 'showlogin', 'showmap', 'showmsg', 'showpost', 'showroom', 'shows',
    'showthread', 'shtml', 'si', 'sid', 'sign', 'sign_up', 'signature', 'signaturepics', 'signed', 'signer', 'signin', 'signing',
    'signoff', 'signon', 'signout', 'signup', 'sign-up', 'simple', 'simplelogin', 'simpleLogin', 'single', 'single_pages', 'sink', 'site',
    'site_map', 'siteadmin', 'sitebuilder', 'sitecore', 'sitefiles', 'siteimages', 'sitemap', 'site-map', 'SiteMap', 'sitemap.gz', 'sitemap.xml', 'sitemaps',
    'sitemgr', 'sites', 'Sites', 'SiteScope', 'sitesearch', 'SiteServer', 'sk', 'skel', 'skin', 'skin1', 'skin1_original', 'skins',
    'skip', 'sl', 'slabel', 'slashdot', 'slide_show', 'slides', 'slideshow', 'slimstat', 'sling', 'sm', 'small', 'smarty',
    'smb', 'smblogin', 'smf', 'smile', 'smiles', 'smileys', 'smilies', 'sms', 'smtp', 'snippets', 'snoop', 'snp',
    'so', 'soap', 'soapdocs', 'SOAPMonitor', 'soaprouter', 'social', 'soft', 'software', 'Software', 'sohoadmin', 'solaris', 'sold',
    'solution', 'solutions', 'solve', 'solved', 'somebody', 'songs', 'sony', 'soporte', 'sort', 'sound', 'sounds', 'source',
    'sources', 'Sources', 'sox', 'sp', 'space', 'spacer', 'spain', 'spam', 'spamlog.log', 'spanish', 'spaw', 'speakers',
    'spec', 'special', 'special_offers', 'specials', 'specified', 'specs', 'speedtest', 'spellchecker', 'sphider', 'spider', 'spiders', 'splash',
    'sponsor', 'sponsors', 'spool', 'sport', 'sports', 'Sports', 'spotlight', 'spryassets', 'Spy', 'spyware', 'sq', 'sql',
    'SQL', 'sqladmin', 'sql-admin', 'sqlmanager', 'sqlnet', 'sqlweb', 'squelettes', 'squelettes-dist', 'squirrel', 'squirrelmail', 'sr', 'src',
    'srchad', 'srv', 'ss', 'ss_vms_admin_sm', 'ssfm', 'ssh', 'sshadmin', 'ssi', 'ssl', 'ssl_check', 'sslvpn', 'ssn',
    'sso', 'ssp_director', 'st', 'stackdump', 'staff', 'staff_directory', 'staffs', 'stage', 'staging', 'stale', 'standalone', 'standard',
    'standards', 'star', 'staradmin', 'start', 'starter', 'startpage', 'stat', 'state', 'statement', 'statements', 'states', 'static',
    'staticpages', 'statistic', 'statistics', 'Statistics', 'statistik', 'stats', 'Stats', 'statshistory', 'status', 'statusicon', 'stock', 'stoneedge',
    'stop', 'storage', 'store', 'store_closed', 'stored', 'stores', 'stories', 'story', 'stow', 'strategy', 'stream', 'string',
    'strut', 'struts', 'student', 'students', 'studio', 'stuff', 'style', 'style_avatars', 'style_captcha', 'style_css', 'style_emoticons', 'style_images',
    'styles', 'stylesheet', 'stylesheets', 'sub', 'subdomains', 'subject', 'sub-login', 'submenus', 'submissions', 'submit', 'submitter', 'subs',
    'subscribe', 'subscribed', 'subscriber', 'subscribers', 'subscription', 'subscriptions', 'success', 'suche', 'sucontact', 'suffix', 'suggest', 'suggest-listing',
    'suite', 'suites', 'summary', 'sun', 'sunos', 'SUNWmc', 'super', 'Super-Admin', 'supplier', 'support', 'Support', 'support_login',
    'supported', 'surf', 'survey', 'surveys', 'suspended.page', 'suupgrade', 'sv', 'svc', 'svn', 'svn-base', 'svr', 'sw',
    'swajax1', 'swf', 'swfobject.js', 'swfs', 'switch', 'sws', 'synapse', 'sync', 'synced', 'syndication', 'sys', 'sysadmin',
    'sys-admin', 'SysAdmin', 'sysadmin2', 'SysAdmin2', 'sysadmins', 'sysmanager', 'system', 'system_admin', 'system_administration', 'system_web', 'system-admin', 'system-administration',
    'systems', 'sysuser', 'szukaj', 't', 'T', 't1', 't3lib', 'table', 'tabs', 'tag', 'tagline', 'tags',
    'tail', 'talk', 'talks', 'tape', 'tapes', 'tapestry', 'tar', 'tar.bz2', 'tar.gz', 'target', 'tartarus', 'task',
    'tasks', 'taxonomy', 'tb', 'tcl', 'te', 'team', 'tech', 'technical', 'technology', 'Technology', 'tel', 'tele',
    'television', 'tell_a_friend', 'tell_friend', 'tellafriend', 'temaoversikt', 'temp', 'TEMP', 'templ', 'template', 'templates', 'templates_c', 'templets',
    'temporal', 'temporary', 'temps', 'term', 'terminal', 'terms', 'terms_privacy', 'termsofuse', 'terms-of-use', 'terrorism', 'test', 'test_db',
    'test1', 'test123', 'test1234', 'test2', 'test3', 'test-cgi', 'teste', 'test-env', 'testimonial', 'testimonials', 'testing', 'tests',
    'testsite', 'texis', 'text', 'text-base', 'textobject', 'textpattern', 'texts', 'tgp', 'tgz', 'th', 'thanks', 'thankyou',
    'thank-you', 'the', 'theme', 'themes', 'Themes', 'thickbox', 'third-party', 'this', 'thread', 'threadrate', 'threads', 'threadtag',
    'thumb', 'thumbnail', 'thumbnails', 'thumbs', 'thumbs.db', 'Thumbs.db', 'ticket', 'ticket_list', 'ticket_new', 'tickets', 'tienda', 'tiki',
    'tiles', 'time', 'timeline', 'tiny_mce', 'tinymce', 'tip', 'tips', 'title', 'titles', 'tl', 'tls', 'tmp',
    'TMP', 'tmpl', 'tmps', 'tn', 'tncms', 'to', 'toc', 'today', 'todel', 'todo', 'TODO', 'toggle',
    'tomcat', 'tomcat-docs', 'tool', 'toolbar', 'toolkit', 'tools', 'tooltip', 'top', 'top1', 'topic', 'topicadmin', 'topics',
    'toplist', 'toplists', 'topnav', 'topsites', 'torrent', 'torrents', 'tos', 'tour', 'tours', 'toys', 'tp', 'tpl',
    'tpv', 'tr', 'trac', 'trace', 'traceroute', 'traces', 'track', 'trackback', 'trackclick', 'tracker', 'trackers', 'tracking',
    'trackpackage', 'tracks', 'trade', 'trademarks', 'traffic', 'trailer', 'trailers', 'training', 'trans', 'transaction', 'transactions', 'transfer',
    'transformations', 'translate', 'translations', 'transparent', 'transport', 'trap', 'trash', 'travel', 'Travel', 'treasury', 'tree', 'trees',
    'trends', 'trial', 'true', 'trunk', 'tslib', 'tsweb', 'tt', 'tuning', 'turbine', 'tuscany', 'tutorial', 'tutorials',
    'tv', 'tw', 'twatch', 'tweak', 'twiki', 'twitter', 'tx', 'txt', 'type', 'typo3', 'typo3_src', 'typo3conf',
    'typo3temp', 'typolight', 'u', 'U', 'ua', 'ubb', 'uc', 'uc_client', 'uc_server', 'ucenter', 'ucp', 'uddi',
    'uds', 'ui', 'uk', 'umbraco', 'umbraco_client', 'umts', 'uncategorized', 'under_update', 'uninstall', 'union', 'unix', 'unlock',
    'unpaid', 'unreg', 'unregister', 'unsafe', 'unsubscribe', 'unused', 'up', 'upcoming', 'upd', 'update', 'updated', 'updateinstaller',
    'updater', 'updates', 'updates-topic', 'upgrade', 'upgrade.readme', 'upload', 'upload_file', 'upload_files', 'uploaded', 'uploadedfiles', 'uploadedimages', 'uploader',
    'uploadfile', 'uploadfiles', 'uploads', 'ur-admin', 'urchin', 'url', 'urlrewriter', 'urls', 'us', 'US', 'usa', 'usage',
    'user', 'user_upload', 'useradmin', 'userapp', 'usercontrols', 'usercp', 'usercp2', 'userdir', 'userfiles', 'UserFiles', 'userimages', 'userinfo',
    'userlist', 'userlog', 'userlogin', 'usermanager', 'username', 'usernames', 'usernote', 'users', 'usr', 'usrmgr', 'usrs', 'ustats',
    'usuario', 'usuarios', 'util', 'utilities', 'Utilities', 'utility', 'utility_login', 'utils', 'v', 'V', 'v1', 'v2',
    'v3', 'v4', 'vadmind', 'validation', 'validatior', 'vap', 'var', 'vault', 'vb', 'vbmodcp', 'vbs', 'vbscript',
    'vbscripts', 'vbseo', 'vbseocp', 'vcss', 'vdsbackup', 'vector', 'vehicle', 'vehiclemakeoffer', 'vehiclequote', 'vehicletestdrive', 'velocity', 'venda',
    'vendor', 'vendors', 'ver', 'ver1', 'ver2', 'version', 'verwaltung', 'vfs', 'vi', 'viagra', 'vid', 'video',
    'Video', 'videos', 'view', 'view_cart', 'viewcart', 'viewcvs', 'viewer', 'viewfile', 'viewforum', 'viewlogin', 'viewonline', 'views',
    'viewsource', 'view-source', 'viewsvn', 'viewthread', 'viewtopic', 'viewvc', 'vip', 'virtual', 'virus', 'visit', 'visitor', 'visitormessage',
    'vista', 'vm', 'vmailadmin', 'void', 'voip', 'vol', 'volunteer', 'vote', 'voted', 'voter', 'votes', 'vp',
    'vpg', 'vpn', 'vs', 'vsadmin', 'vuln', 'vvc_display', 'w', 'W', 'w3', 'w3c', 'w3svc', 'W3SVC',
    'W3SVC1', 'W3SVC2', 'W3SVC3', 'wa', 'wallpaper', 'wallpapers', 'wap', 'war', 'warenkorb', 'warez', 'warn', 'way-board',
    'wbboard', 'wbsadmin', 'wc', 'wcs', 'wdav', 'weather', 'web', 'web.config', 'web.xml', 'web_users', 'web1', 'web2',
    'web3', 'webaccess', 'webadm', 'webadmin', 'WebAdmin', 'webagent', 'webalizer', 'webapp', 'webapps', 'webb', 'webbbs', 'web-beans',
    'webboard', 'webcalendar', 'webcam', 'webcart', 'webcast', 'webcasts', 'webcgi', 'webcharts', 'webchat', 'web-console', 'webctrl_client', 'webdata',
    'webdav', 'webdb', 'webdist', 'webedit', 'webfm_send', 'webhits', 'webim', 'webinar', 'web-inf', 'WEB-INF', 'weblog', 'weblogic',
    'weblogs', 'webmail', 'webmaster', 'webmasters', 'webpages', 'webplus', 'webresource', 'websearch', 'webservice', 'webservices', 'webshop', 'website',
    'websites', 'websphere', 'websql', 'webstat', 'webstats', 'websvn', 'webtrends', 'webusers', 'webvpn', 'webwork', 'wedding', 'week',
    'weekly', 'welcome', 'well', 'wellcome', 'werbung', 'wget', 'what', 'whatever', 'whatnot', 'whatsnew', 'white', 'whitepaper',
    'whitepapers', 'who', 'whois', 'wholesale', 'whosonline', 'why', 'wicket', 'wide_search', 'widget', 'widgets', 'wifi', 'wii',
    'wiki', 'will', 'win', 'win32', 'windows', 'Windows', 'wink', 'winnt', 'wireless', 'wishlist', 'with', 'wiz',
    'wizard', 'wizmysqladmin', 'wml', 'wolthuis', 'word', 'wordpress', 'work', 'workarea', 'workflowtasks', 'working', 'workplace', 'works',
    'workshop', 'workshops', 'world', 'worldpayreturn', 'worldwide', 'wow', 'wp', 'wp-admin', 'wp-app', 'wp-atom', 'wpau-backup', 'wp-blog-header',
    'wpcallback', 'wp-comments', 'wp-commentsrss2', 'wp-config', 'wpcontent', 'wp-content', 'wp-cron', 'wp-dbmanager', 'wp-feed', 'wp-icludes', 'wp-images', 'wp-includes',
    'wp-links-opml', 'wp-load', 'wp-login', 'wp-mail', 'wp-pass', 'wp-rdf', 'wp-register', 'wp-rss', 'wp-rss2', 'wps', 'wp-settings', 'wp-signup',
    'wp-syntax', 'wp-trackback', 'wrap', 'writing', 'ws', 'ws_ftp', 'WS_FTP', 'WS_FTP.LOG', 'ws-client', 'wsdl', 'wss', 'wstat',
    'wstats', 'wt', 'wtai', 'wusage', 'wwhelp', 'www', 'www1', 'www2', 'www3', 'wwwboard', 'wwwjoin', 'wwwlog',
    'wwwroot', 'www-sql', 'wwwstat', 'wwwstats', 'wwwthreads', 'wwwuser', 'wysiwyg', 'wysiwygpro', 'x', 'X', 'xajax', 'xajax_js',
    'xalan', 'xbox', 'xcache', 'xcart', 'xd_receiver', 'xdb', 'xerces', 'xfer', 'xhtml', 'xlogin', 'xls', 'xmas',
    'xml', 'XML', 'xmlfiles', 'xmlimporter', 'xmlrpc', 'xml-rpc', 'xmlrpc.php', 'xmlrpc_server', 'xmlrpc_server.php', 'xn', 'xsl', 'xslt',
    'xsql', 'xx', 'xxx', 'XXX', 'xyz', 'xyzzy', 'y', 'yahoo', 'year', 'yearly', 'yesterday', 'yml',
    'yonetici', 'yonetim', 'youtube', 'yshop', 'yt', 'yui', 'z', 'zap', 'zboard', 'zencart', 'zend', 'zero',
    'zeus', 'zh', 'zh_CN', 'zh_TW', 'zh-cn', 'zh-tw', 'zimbra', 'zip', 'zipfiles', 'zips', 'zoeken', 'zone',
    'zones', 'zoom', 'zope', 'zorum', 'zt',
]
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
