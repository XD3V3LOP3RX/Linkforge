import base64
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import core


class Tests(unittest.TestCase):
    def test_csv_part_and_protocol(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'input.csv'
            p.write_text('Title,Part,Link\nExample,Update v1.2 : Mirror,//1fichier.com/?abc\n', encoding='utf-8')
            self.assertEqual(core.read_entries(p), [('https://1fichier.com/?abc', 'Example [Update v1.2]')])

    def test_text_names_and_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'input.txt'
            p.write_text('Game DLC | https://example.com/a\nGame DLC | https://example.com/a\nGame Update https://example.com/b\n', encoding='utf-8')
            self.assertEqual(len(core.read_entries(p)), 2)
            self.assertEqual(core.read_entries(p)[0][1], 'Game DLC')

    def test_unicode_and_xml(self):
        root = ET.fromstring(core.make_xml('Names & labels', [('https://example.com/?a=1&b=2', 'Café [DLC].rar')]))
        name = root.findtext('./content/package/file/filename')
        self.assertEqual(base64.b64decode(name).decode(), 'Café [DLC].rar')

    def test_service_failure_preserves_output(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'old.dlc'
            p.write_bytes(b'keep original')
            with patch('core.requests.post', side_effect=RuntimeError('offline')):
                with self.assertRaises(RuntimeError):
                    core.create('Test', [('https://example.com/a', 'Name')], p)
            self.assertEqual(p.read_bytes(), b'keep original')

    def test_empty_input(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'empty.txt'
            p.write_text('')
            with self.assertRaises(ValueError):
                core.read_entries(p)

    def test_mixed_hosts_and_pasted_names(self):
        entries = core.parse_text('Example update | https://example.org/update.zip\nhttps://files.example.net/a https://1fichier.com/?abc\n')
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0][1], 'Example update')
        self.assertEqual(entries[1][0], 'https://files.example.net/a')

    def test_uppercase_scheme(self):
        entries = core.parse_text('Named file | HTTPS://example.org/file.zip')
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0][1], 'Named file')

    def test_text_ignores_notes_and_normalizes_protocol_relative_links(self):
        text = 'Download list\n\nhttps://example.org/a.zip\nnot a URL\n//1fichier.com/?example\nEnd of list\n'
        self.assertEqual(core.parse_text(text), [
            ('https://example.org/a.zip', 'https://example.org/a.zip'),
            ('https://1fichier.com/?example', 'https://1fichier.com/?example')])

    def test_arbitrary_text_does_not_become_a_filename(self):
        entries = core.parse_text('Download: https://example.org/a.zip\n<a href="https://example.net/b.zip">File</a>\n# https://example.com/c.zip')
        self.assertEqual(len(entries), 3)
        self.assertTrue(all(url == name for url, name in entries))

    def test_invalid_candidates_do_not_block_valid_links(self):
        entries = core.parse_text('https:// https:///broken\nActual | //example.org/a.zip')
        self.assertEqual(entries, [('https://example.org/a.zip', 'Actual')])

    def test_no_links_has_clear_error(self):
        with self.assertRaisesRegex(ValueError, 'No valid HTTP/HTTPS links'):
            core.parse_text('just notes\nno links')

    def test_public_example_list(self):
        entries = core.read_entries(Path(__file__).parent / 'examples' / 'sample-links.csv')
        self.assertEqual(len(entries), 3)
        self.assertEqual(len({core.urlsplit(url).hostname for url, _ in entries}), 3)
        self.assertTrue(all(core.urlsplit(url).hostname in ('example.com', 'example.org', 'example.net') for url, _ in entries))


if __name__ == '__main__':
    unittest.main()
