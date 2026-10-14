"""Named DLC containers compatible with JDownloader. No downloads are started."""
import base64
import csv
import io
import os
from pathlib import Path
import re
import secrets
import tempfile
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

import requests
from Crypto.Cipher import AES

SERVICE = 'https://service.jdownloader.org/dlcrypt/service.php'
PYLO_KEY = b'cb99b5cbc24db398'
PYLO_IV = b'9bc24cb995cb8db3'


def encode(text):
    return base64.b64encode(text.encode('utf-8')).decode('ascii')


def normalize_url(url):
    url = url.strip()
    if url.startswith('//'):
        url = 'https:' + url
    p = urlsplit(url)
    if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password:
        raise ValueError('Each link must be a valid HTTP or HTTPS URL.')
    return url


def parse_text(text):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        matches = list(re.finditer(r'https?://[^\s|<>"\']+|(?<![\w:/])//[^\s|<>"\']+', line, re.IGNORECASE))
        for match in matches:
            # Only explicit "Name | URL" input assigns a display name.
            # Surrounding prose, HTML, and headings must not become filenames.
            prefix = line[:match.start()].rstrip()
            name = prefix[:-1].strip() if len(matches) == 1 and prefix.endswith('|') else ''
            try:
                url = normalize_url(match.group())
            except ValueError:
                continue
            rows.append((url, name or url))
    if not rows:
        raise ValueError('No valid HTTP/HTTPS links found. Paste URLs or import a file containing links.')
    return list(dict.fromkeys(rows))


def read_entries(path, include_packages=False):
    text = Path(path).read_text(encoding='utf-8-sig')
    rows = []
    if Path(path).suffix.lower() == '.csv':
        reader = csv.DictReader(io.StringIO(text))
        columns = {c.strip().lower(): c for c in (reader.fieldnames or [])}
        urlcol = next((columns[c] for c in ('link', 'url', 'links') if c in columns), None)
        namecol = next((columns[c] for c in ('title', 'name', 'game') if c in columns), None)
        if not urlcol:
            raise ValueError('CSV needs a Link or URL column; Title or Name is optional.')
        for n, row in enumerate(reader, 2):
            url = (row.get(urlcol) or '').strip()
            if not url:
                continue
            name = (row.get(namecol) or '').strip() if namecol else ''
            part = (row.get(columns.get('part')) or '').split(' :', 1)[0].strip(' :–—-')
            if part:
                name += ' [' + part + ']'
            packagecol = columns.get('package') or columns.get('package name')
            package = (row.get(packagecol) or '').strip() if packagecol else ''
            rows.append((url, name, package))
    else:
        rows = [(url, name, '') for url, name in parse_text(text)]
    entries, seen = [], set()
    for url, name, package in rows:
        url = normalize_url(url)
        key = (url, name, package) if include_packages else (url, name)
        if key not in seen:
            seen.add(key)
            entries.append({'url': url, 'name': name or url, 'package': package} if include_packages else (url, name or url))
    if not entries:
        raise ValueError('No links found in this file.')
    return entries


def make_xml(package, entries):
    root = ET.Element('dlc')
    header = ET.SubElement(root, 'header')
    generator = ET.SubElement(header, 'generator')
    for tag, value in [('app', 'JDownloader'), ('version', '48637'), ('url', 'http://jdownloader.org')]:
        ET.SubElement(generator, tag).text = encode(value)
    ET.SubElement(header, 'tribute')
    ET.SubElement(header, 'dlcxmlversion').text = encode('20_02_2008')
    content = ET.SubElement(root, 'content')
    pkg = ET.SubElement(content, 'package', name=encode(package), comment='', category=encode('various'))
    for url, name in entries:
        node = ET.SubElement(pkg, 'file')
        for tag, value in [('url', url), ('filename', name), ('size', '0')]:
            ET.SubElement(node, tag).text = encode(value)
    return ET.tostring(root, encoding='utf-8')


def service_token(response):
    response.raise_for_status()
    match = re.search(r'<rc>(.*?)</rc>', response.text, re.S)
    if not match:
        raise ValueError('JDownloader key service returned an unexpected reply. Try again later.')
    return match.group(1).strip()


def decrypt_root(data):
    """Decrypt DLC XML without following any of the embedded download links."""
    if len(data) > 64 * 1024 * 1024:
        raise ValueError('This container exceeds the 64 MB safety limit.')
    data = b''.join(data.split())
    if len(data) <= 88:
        raise ValueError('Not a valid DLC container: file is empty or incomplete.')
    token, blob = data[-88:], base64.b64decode(data[:-88], validate=True)
    if not blob or len(blob) % 16:
        raise ValueError('Not a valid DLC container: encrypted data is incomplete.')
    reply = requests.get(SERVICE, params={'srcType': 'dlc', 'destType': 'pylo', 'data': token.decode('ascii')}, timeout=(10, 45))
    rc = base64.b64decode(service_token(reply), validate=True)[:16]
    if len(rc) != 16:
        raise ValueError('Invalid verification key from JDownloader.')
    key = AES.new(PYLO_KEY, AES.MODE_CBC, PYLO_IV).decrypt(rc)
    plain = AES.new(key, AES.MODE_CBC, key).decrypt(blob)
    # Official writers use spaces; some compatible writers use PKCS#7.
    padding = plain[-1]
    if 1 <= padding <= 16 and plain.endswith(bytes([padding]) * padding):
        plain = plain[:-padding]
    xml = base64.b64decode(b''.join(plain.split()), validate=True)
    if b'<!DOCTYPE' in xml.upper() or b'<!ENTITY' in xml.upper():
        raise ValueError('Unsupported XML declarations in container.')
    root = ET.fromstring(xml)
    if root.tag != 'dlc' or root.find('content') is None:
        raise ValueError('Unsupported DLC document structure.')
    return root


def decode_field(value, default=''):
    if not value:
        return default
    return base64.b64decode(''.join(value.split()), validate=True).decode('utf-8')


def read_dlc(path):
    """Return all packages and files as explicit metadata rows."""
    source = Path(path)
    if source.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('This container exceeds the 64 MB safety limit.')
    root = decrypt_root(source.read_bytes())
    rows = []
    for package in root.findall('./content/package'):
        package_name = decode_field(package.get('name'))
        for file in package.findall('file'):
            url = decode_field(file.findtext('url')).strip()
            if not url:
                raise ValueError('A DLC file entry is missing its URL. Import stopped; nothing was added.')
            rows.append({'url': url, 'name': decode_field(file.findtext('filename'), url), 'package': package_name})
    if not rows:
        raise ValueError('This DLC contains no downloadable links.')
    return rows


def decrypt(data):
    """Verify package name AND every URL/filename through JD's key service."""
    root = decrypt_root(data)
    pkgs = root.findall('./content/package')
    if len(pkgs) != 1:
        raise ValueError('Expected one package during verification.')
    pkg = pkgs[0]
    entries = [(base64.b64decode(f.findtext('url')).decode('utf-8'),
                base64.b64decode(f.findtext('filename')).decode('utf-8')) for f in pkg.findall('file')]
    return base64.b64decode(pkg.get('name')).decode('utf-8'), entries


def export_collection(rows, destination, kind='csv'):
    """Export extracted metadata, never fetch an embedded download URL."""
    if kind == 'csv':
        buffer = io.StringIO(newline='')
        writer = csv.writer(buffer)
        writer.writerow(['Title', 'Package', 'Link'])
        writer.writerows((row['name'], row.get('package', ''), row['url']) for row in rows)
        data = buffer.getvalue().encode('utf-8-sig')
    elif kind == 'txt':
        if any('\n' in row['url'] or '\r' in row['url'] for row in rows):
            raise ValueError('A URL contains a line break. Export to CSV to preserve it safely.')
        data = ''.join(row['url'] + '\n' for row in rows).encode('utf-8')
    else:
        raise ValueError('Choose CSV or TXT export.')
    target = Path(destination)
    fd, temporary = tempfile.mkstemp(dir=target.parent, suffix='.tmp')
    try:
        with os.fdopen(fd, 'wb') as file:
            file.write(data)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def create(package, entries, destination, verify=True, progress=lambda text: None):
    if not package.strip() or not entries:
        raise ValueError('Choose a package name and load some links first.')
    progress('Encrypting names and links…')
    plain = base64.b64encode(make_xml(package, entries))
    plain += b' ' * (-len(plain) % 16)
    key = secrets.token_hex(8).encode('ascii')
    body = base64.b64encode(AES.new(key, AES.MODE_CBC, key).encrypt(plain))
    progress('Contacting JDownloader key service…')
    reply = requests.post(SERVICE, data={'jd': '1', 'srcType': 'plain', 'data': key.decode('ascii')}, timeout=(10, 45))
    token = service_token(reply)
    if len(token) != 88:
        raise ValueError('JDownloader returned an invalid container key.')
    data = body + token.encode('ascii')
    if verify:
        progress('Verifying every link and display name…')
        if decrypt(data) != (package, entries):
            raise ValueError('Round-trip check failed. Output was not saved.')
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=target.parent, suffix='.tmp')
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
        os.replace(temp, target)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    progress('Ready — import your DLC in JDownloader.')
    return len(data)
