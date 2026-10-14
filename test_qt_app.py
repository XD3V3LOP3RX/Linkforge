import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QAbstractItemView, QFileDialog, QDialog
from PySide6.QtGui import QFontDatabase
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
import qt_app


APP = QApplication.instance() or QApplication([])
APP.setStyle('Fusion')
fonts = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
for name in ('segoeui.ttf', 'segoeuib.ttf'):
    if (fonts / name).is_file():
        QFontDatabase.addApplicationFont(str(fonts / name))
APP.setStyleSheet(qt_app.STYLE.replace('CHECK_PATH', (qt_app.ASSETS / 'check.png').as_posix()).replace('CHEVRON_PATH', (qt_app.ASSETS / 'chevron.png').as_posix()))


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.window = qt_app.MainWindow()
        self.entries = [('https://example.org/a.zip', 'Base.zip'), ('https://example.net/u.zip', 'Update.zip')]
        self.window.show()
        APP.processEvents()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        APP.processEvents()

    def test_empty_state_and_action_availability(self):
        self.assertEqual(self.window.pages.currentIndex(), 1)
        self.assertFalse(self.window.create_button.isEnabled())
        self.assertFalse(self.window.export_button.isEnabled())
        self.window.model.add(self.entries)
        self.assertEqual(self.window.pages.currentIndex(), 0)
        self.assertTrue(self.window.create_button.isEnabled())
        self.assertEqual([w.text() for w in self.window.stat_values], ['2', '2', '2'])

    def test_filter_does_not_limit_export(self):
        self.window.model.add(self.entries)
        self.window.search.setText('Update')
        self.assertEqual(self.window.proxy.rowCount(), 1)
        self.assertEqual(len(self.window.selected_entries()), 2)
        self.window.search.setText('no such entry')
        self.assertEqual(self.window.pages.currentIndex(), 1)
        self.assertEqual(self.window.empty_title.text(), 'No matching links')

    def test_edit_and_remove_filtered_sorted_source_row(self):
        self.window.model.add(self.entries)
        self.window.table.sortByColumn(0, Qt.DescendingOrder)
        self.window.search.setText('Update')
        proxy = self.window.proxy.index(0, 0)
        source = self.window.proxy.mapToSource(proxy)
        self.assertTrue(self.window.model.setData(source, 'Update v2.zip'))
        self.window.table.selectRow(0)
        self.window.remove_selected()
        self.assertEqual(self.window.model.entries, self.entries[:1])

    def test_dedup_and_extension(self):
        self.assertEqual(self.window.model.add(self.entries + self.entries), 2)
        self.window.extension.setCurrentIndex(1)
        self.assertEqual(self.window.selected_entries()[0][1], 'Base.zip.rar')
        self.window.extension.setCurrentIndex(0)
        self.assertEqual(self.window.selected_entries(), self.entries)

    def test_paste_validation(self):
        dialog = qt_app.PasteDialog(self.window)
        dialog.editor.setPlainText('not a link')
        dialog.apply()
        self.assertNotEqual(dialog.result(), QDialog.Accepted)
        self.assertTrue(dialog.error.text())
        dialog.editor.setPlainText('Update.zip | https://example.com/u.zip')
        dialog.apply()
        self.assertEqual(dialog.result(), QDialog.Accepted)
        self.assertEqual(dialog.entries[0][1], 'Update.zip')

    def test_import_export_and_explicit_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.csv'
            path.write_text('Title,Link\nBase.zip,https://example.com/base.zip\n', encoding='utf-8')
            self.window.import_paths([str(path)])
            # Qt may expand Windows 8.3 paths; compare directory identity, not spelling.
            self.assertTrue(self.window.dialog_dir.samefile(path.parent))
            with patch('qt_app.QFileDialog.getOpenFileNames', return_value=([], '')) as picker:
                self.window.import_files()
            self.assertTrue(Path(picker.call_args.args[2]).samefile(directory))
            self.assertEqual(picker.call_args.kwargs['options'], QFileDialog.DontUseNativeDialog)
            output = Path(directory) / 'out.csv'
            with patch.object(self.window, 'choose_output', return_value=str(output)):
                self.window.export_list()
            self.assertEqual(qt_app.core.read_entries(output), self.window.model.entries)

    def test_minimum_window_controls_not_compressed(self):
        self.window.resize(1080, 740)
        APP.processEvents()
        self.assertGreaterEqual(self.window.package.height(), 40)
        self.assertGreaterEqual(self.window.extension.height(), 40)
        self.assertGreaterEqual(self.window.create_button.height(), 44)
        self.assertGreaterEqual(self.window.export_button.height(), 32)
        self.assertTrue(self.window.settings.rect().contains(self.window.export_button.geometry()))
        self.assertGreaterEqual(self.window.notice.height(), self.window.notice.sizeHint().height())

    def test_suffix_precedes_overwrite_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            self.window.dialog_dir = Path(directory)
            for suffix in ('csv', 'dlc'):
                existing = Path(directory) / ('existing.' + suffix)
                existing.write_text('original')
                dialog = self.window.make_save_dialog('Save', 'existing', suffix, '*.' + suffix)
                self.assertEqual(dialog.defaultSuffix(), suffix)
                self.assertTrue(Path(dialog.selectedFiles()[0]).samefile(existing))
                self.assertFalse(dialog.testOption(QFileDialog.DontConfirmOverwrite))
                dialog.deleteLater()
                self.assertEqual(existing.read_text(), 'original')

    def wait_for_worker(self):
        for _ in range(200):
            APP.processEvents()
            if not self.window.is_busy():
                break
            QTest.qWait(10)
        APP.processEvents()
        self.assertFalse(self.window.is_busy())

    def test_dlc_async_import_preserves_packages_and_exports(self):
        rows = [{'url': 'https://example.com/a.zip', 'name': 'Base.zip', 'package': 'Base'},
                {'url': 'https://example.net/u.zip', 'name': 'Update.zip', 'package': 'Updates'}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.dlc'
            with patch('qt_app.core.read_dlc', return_value=rows):
                self.window.import_paths([str(path)])
                self.wait_for_worker()
            self.assertEqual(self.window.model.package_names, ['Base', 'Updates'])
            self.assertEqual(self.window.model.data(self.window.model.index(1, 1)), 'Updates')
            self.window.search.setText('Updates')
            self.assertEqual(self.window.proxy.rowCount(), 1)
            for kind in ('csv', 'txt'):
                target = Path(directory) / ('export.' + kind)
                with patch.object(self.window, 'choose_output', return_value=str(target)):
                    self.window.export_list(kind)
                if kind == 'csv':
                    self.assertEqual(qt_app.core.read_entries(target, include_packages=True), rows)
                else:
                    self.assertEqual(target.read_text().splitlines(), [row['url'] for row in rows])

    def test_dlc_failure_leaves_collection_unchanged(self):
        self.window.model.add(self.entries, ['Original', 'Original'])
        with patch('qt_app.core.read_dlc', side_effect=ValueError('corrupt container')), patch('qt_app.QMessageBox.warning') as warning:
            self.window.import_paths(['broken.dlc'])
            self.wait_for_worker()
        warning.assert_called_once()
        self.assertEqual(self.window.model.entries, self.entries)
        self.assertEqual(self.window.model.package_names, ['Original', 'Original'])

    def test_duplicate_url_in_distinct_packages_keeps_both(self):
        self.window.model.add([self.entries[0], self.entries[0]], ['First', 'Second'])
        self.assertEqual(len(self.window.model.entries), 2)
        self.window.model.setData(self.window.model.index(0, 0), 'Renamed.zip')
        self.assertEqual(self.window.model.package_names, ['First', 'Second'])
        self.window.table.selectRow(0)
        self.window.remove_selected()
        self.assertEqual(self.window.model.package_names, ['Second'])

    def test_readable_url_and_click_keep_original_encoding(self):
        original = 'https://example.com/downloads/1080%C2%B0%20Sample%20%5Bv2%5D.7z'
        self.window.model.add([(original, 'Sample.7z')])
        source = self.window.model.index(0, 3)
        self.assertIn('1080° Sample [v2].7z', self.window.model.data(source))
        self.assertEqual(self.window.model.data(source, Qt.EditRole), original)
        proxy = self.window.proxy.mapFromSource(source)
        APP.processEvents()
        self.window.table.scrollTo(proxy)
        APP.processEvents()
        with patch('qt_app.QDesktopServices.openUrl', return_value=True) as browser:
            QTest.mouseClick(self.window.table.viewport(), Qt.LeftButton, pos=self.window.table.visualRect(proxy).center())
        browser.assert_called_once()
        self.assertEqual(bytes(browser.call_args.args[0].toEncoded()).decode(), original)
        self.assertEqual(self.window.selected_entries()[0][0], original)

    def test_sorted_link_click_opens_correct_row_and_names_do_not_open(self):
        self.window.model.add(self.entries)
        self.window.table.sortByColumn(0, Qt.DescendingOrder)
        with patch('qt_app.QDesktopServices.openUrl', return_value=True) as browser:
            self.window.open_clicked_link(self.window.proxy.index(0, 0))
            browser.assert_not_called()
            self.window.open_clicked_link(self.window.proxy.index(0, 3))
        self.assertEqual(browser.call_args.args[0].toString(), self.entries[1][0])

    def test_non_web_link_not_launched(self):
        self.window.model.add([('file:///C:/example.exe', 'Not a web link')])
        with patch('qt_app.QDesktopServices.openUrl') as browser:
            self.window.open_row_link(0)
        browser.assert_not_called()

    def test_copy_and_export_keep_encoded_url(self):
        original = 'https://example.com/a%20b%5B1%5D.zip?token=a%2Bb&file=x%2520y'
        self.window.model.add([(original, 'A file.zip')])
        with patch('qt_app.QApplication.clipboard') as clipboard:
            self.window.copy_row_link(0)
            clipboard.return_value.setText.assert_called_once_with(original)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'links.txt'
            with patch.object(self.window, 'choose_output', return_value=str(target)):
                self.window.export_list('txt')
            self.assertEqual(target.read_text().strip(), original)

    def test_background_build(self):
        self.window.model.add(self.entries)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'out.dlc'
            def fake_create(package, entries, destination, verify, progress):
                progress('Checking test data')
                Path(destination).write_bytes(b'test-container')
            with patch.object(self.window, 'choose_output', return_value=str(path)), patch('qt_app.core.create', side_effect=fake_create):
                self.window.build()
                for _ in range(200):
                    APP.processEvents()
                    if not self.window.is_busy():
                        break
                    QTest.qWait(10)
                APP.processEvents()
            self.assertFalse(self.window.is_busy())
            self.assertEqual(self.window.output, str(path))
            self.assertTrue(self.window.create_button.isEnabled())
            self.assertEqual(path.read_bytes(), b'test-container')


if __name__ == '__main__':
    unittest.main()
