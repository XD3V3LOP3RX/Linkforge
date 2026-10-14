import base64
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

from Crypto.Cipher import AES
import core

KEY = b'0123456789abcdef'


def envelope(xml):
    plain = base64.b64encode(xml)
    plain += b' ' * (-len(plain) % 16)
    return base64.b64encode(AES.new(KEY, AES.MODE_CBC, KEY).encrypt(plain)) + b'X' * 88


def service_reply():
    reply = Mock()
    rc = AES.new(core.PYLO_KEY, AES.MODE_CBC, core.PYLO_IV).encrypt(KEY)
    reply.text = '<rc>' + base64.b64encode(rc).decode() + '</rc>'
    return reply


class ContainerTests(unittest.TestCase):
    def multi_package(self):
        root = ET.fromstring(core.make_xml('Base & extras', [('https://example.com/base.zip', 'Base, café.zip')]))
        other = ET.fromstring(core.make_xml('Updates', [('https://example.net/update.zip', 'Update v2.zip')]))
        root.find('content').append(other.find('./content/package'))
        return ET.tostring(root)

    def test_extract_multiple_packages_without_fetching_links(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.dlc'
            # A line-wrapped container must also import correctly.
            data = envelope(self.multi_package())
            path.write_bytes(b'\r\n'.join(data[i:i+80] for i in range(0, len(data), 80)))
            with patch('core.requests.get', return_value=service_reply()) as get:
                rows = core.read_dlc(path)
            self.assertEqual(rows, [
                {'url': 'https://example.com/base.zip', 'name': 'Base, café.zip', 'package': 'Base & extras'},
                {'url': 'https://example.net/update.zip', 'name': 'Update v2.zip', 'package': 'Updates'}])
            self.assertEqual(get.call_count, 1)
            self.assertEqual(get.call_args.args[0], core.SERVICE)

    def test_csv_roundtrip_and_txt_urls_only(self):
        rows = [dict(url='https://example.com/a.zip', name='A, file.zip', package='First'),
                dict(url='https://example.com/a.zip', name='A, file.zip', package='Second')]
        with tempfile.TemporaryDirectory() as directory:
            csv = Path(directory) / 'links.csv'
            txt = Path(directory) / 'links.txt'
            core.export_collection(rows, csv, 'csv')
            core.export_collection(rows, txt, 'txt')
            self.assertEqual(core.read_entries(csv, include_packages=True), rows)
            self.assertEqual(txt.read_text().splitlines(), [row['url'] for row in rows])

    def test_corrupt_container_rejected_before_network(self):
        with patch('core.requests.get') as get:
            with self.assertRaises(ValueError):
                core.decrypt_root(b'not a container')
            get.assert_not_called()

    def test_unsafe_xml_rejected(self):
        xml = b'<!DOCTYPE dlc [<!ENTITY x "hello">]><dlc><content/></dlc>'
        with patch('core.requests.get', return_value=service_reply()):
            with self.assertRaisesRegex(ValueError, 'declarations'):
                core.decrypt_root(envelope(xml))

    def test_missing_filename_falls_back_to_url(self):
        root = ET.fromstring(core.make_xml('Package', [('https://example.com/file.zip', 'File')]))
        file = root.find('./content/package/file')
        file.remove(file.find('filename'))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test.dlc'
            path.write_bytes(envelope(ET.tostring(root)))
            with patch('core.requests.get', return_value=service_reply()):
                self.assertEqual(core.read_dlc(path)[0]['name'], 'https://example.com/file.zip')

    def test_multi_package_not_silently_flattened_by_verifier(self):
        with patch('core.requests.get', return_value=service_reply()):
            with self.assertRaisesRegex(ValueError, 'one package'):
                core.decrypt(envelope(self.multi_package()))

    def test_invalid_txt_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'out.txt'
            target.write_text('original')
            with self.assertRaisesRegex(ValueError, 'line break'):
                core.export_collection([{'url': 'https://example.com/\nurl', 'name': 'Name'}], target, 'txt')
            self.assertEqual(target.read_text(), 'original')


if __name__ == '__main__':
    unittest.main()
