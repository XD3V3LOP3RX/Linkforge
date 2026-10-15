"""LinkForge 2 — general-purpose named JDownloader container studio."""
import os
from pathlib import Path
import sys
from urllib.parse import unquote
from html import escape

from PySide6.QtCore import (QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel,
                            QThread, Signal, QUrl)
from PySide6.QtGui import QIcon, QDesktopServices, QKeySequence, QShortcut, QFontDatabase
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QFrame, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QTableView, QHeaderView,
    QAbstractItemView, QFileDialog, QMessageBox, QDialog, QPlainTextEdit,
    QCheckBox, QComboBox, QStackedWidget, QProgressBar, QDialogButtonBox, QMenu)

import core
STYLE = '''
* { font-family: "Segoe UI"; font-size: 13px; color: #dce5f2; }
QMainWindow, QDialog { background: #10141d; }
QWidget#surface { background: #10141d; }
QFrame#sidebar { background: #141a25; border-right: 1px solid #252e3e; }
QFrame#card { background: #171e2b; border: 1px solid #293346; border-radius: 12px; }
QFrame#separator { background: #293346; max-height: 1px; }
QLabel { background: transparent; border: none; }
QLabel#brand { color: #f4f7fc; font-size: 22px; font-weight: 700; }
QLabel#heading { color: #f4f7fc; font-size: 29px; font-weight: 650; }
QLabel#section { color: #f0f4fb; font-size: 16px; font-weight: 600; }
QLabel#muted { color: #8d9cb3; }
QLabel#eyebrow { color: #8090a9; font-size: 10px; font-weight: 700; letter-spacing: 2px; }
QLabel#value { color: #eef3fb; font-size: 25px; font-weight: 600; }
QLabel#badge { background: #18392f; color: #7ee5bc; padding: 5px 9px; border-radius: 6px; font-size: 11px; }
QLabel#notice { background: #192b30; color: #89cfc0; border: 1px solid #2c4947; border-radius: 8px; padding: 10px; }
QPushButton { background: #232d3e; border: 1px solid #354158; border-radius: 7px; padding: 9px 13px; font-weight: 600; }
QPushButton:hover { background: #2d3b51; border-color: #546783; }
QPushButton:pressed { background: #1b2639; }
QPushButton:disabled { background: #1c2330; color: #5c6b82; border-color: #273044; }
QPushButton#primary { background: #72e0b9; color: #0c2b21; border-color: #72e0b9; }
QPushButton#primary:hover { background: #97edce; border-color: #97edce; }
QPushButton#primary:disabled { background: #25483f; color: #76988d; border-color: #25483f; }
QPushButton#subtle { background: transparent; border-color: transparent; color: #9eb0ca; }
QPushButton#subtle:hover { background: #222d3e; color: #e2eaf6; }
QPushButton#nav { background: #233345; border: none; color: #9aeacb; text-align: left; padding: 12px; }
QLineEdit, QPlainTextEdit, QComboBox { background: #101722; border: 1px solid #354158; border-radius: 7px; padding: 9px; selection-background-color: #2e655e; }
QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus { border-color: #72e0b9; }
QLineEdit:disabled { color: #61728c; }
QComboBox::drop-down { border: none; width: 25px; }
QComboBox::down-arrow { image: url("CHEVRON_PATH"); width: 14px; height: 14px; }
QComboBox QAbstractItemView { background: #202b3d; selection-background-color: #345247; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 17px; height: 17px; border: 1px solid #51617b; border-radius: 4px; background: #101722; }
QCheckBox::indicator:checked { background: #72e0b9; border-color: #72e0b9; image: url("CHECK_PATH"); }
QTableView { background: #171e2b; alternate-background-color: #192231; border: none; gridline-color: #263143; selection-background-color: #25453f; selection-color: #eefaf5; outline: none; }
QTableView::item { border-bottom: 1px solid #232e40; padding: 8px; }
QHeaderView::section { background: #1c2534; color: #91a2bb; border: none; border-bottom: 1px solid #303b50; padding: 12px 8px; font-size: 11px; font-weight: 600; }
QTableView QLineEdit { padding: 3px; border-radius: 0; }
QScrollBar:vertical { background: #171e2b; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #38465d; border-radius: 4px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal { background: #171e2b; height: 10px; }
QScrollBar::handle:horizontal { background: #38465d; border-radius: 4px; min-width: 30px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QToolTip { background: #263449; color: #edf3fc; border: 1px solid #53617b; padding: 7px; }
QProgressBar { background: #222e40; border: none; border-radius: 3px; max-height: 5px; }
QProgressBar::chunk { background: #72e0b9; border-radius: 3px; }
QStatusBar { background: #141a25; color: #8d9cb3; border-top: 1px solid #252e3e; }
QStatusBar::item { border: none; }
QFileDialog QListView, QFileDialog QTreeView { background: #171e2b; border: 1px solid #354158; }
QMenu { background: #1c2534; border: 1px solid #354158; padding: 5px; }
QMenu::item { padding: 7px 20px; }
QMenu::item:selected { background: #304858; }
'''

ASSETS = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))


def label(text, role=None, wrap=False):
    widget = QLabel(text)
    if role:
        widget.setObjectName(role)
    widget.setWordWrap(wrap)
    return widget


def button(text, callback, primary=False, subtle=False):
    widget = QPushButton(text)
    widget.setCursor(Qt.PointingHandCursor)
    if primary or subtle:
        widget.setObjectName('primary' if primary else 'subtle')
    widget.clicked.connect(callback)
    return widget


def card():
    widget = QFrame()
    widget.setObjectName('card')
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(14)
    return widget, layout


class LinkModel(QAbstractTableModel):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self.entries = []
        self.package_names = []

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.entries)

    def columnCount(self, parent=QModelIndex()):
        return 4

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ['DISPLAY NAME', 'PACKAGE', 'HOST', 'SOURCE URL'][section]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        url, name = self.entries[index.row()]
        if role == Qt.ToolTipRole and index.column() == 3:
            return '<qt>Click to open in your browser. Right-click to copy.<br><br><b>Original URL:</b><br>' + escape(url) + '</qt>'
        if role in (Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole):
            shown_url = unquote(url) if role == Qt.DisplayRole else url
            return [name, self.package_names[index.row()], core.urlsplit(url).hostname or '', shown_url][index.column()]
        if role == Qt.FontRole and index.column() == 3:
            from PySide6.QtGui import QFont
            font = QFont('Segoe UI', 10)
            font.setUnderline(True)
            return font
        if role == Qt.ForegroundRole and index.column() != 0:
            from PySide6.QtGui import QColor
            return QColor('#8dbbff' if index.column() == 3 else '#94a5be')

    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 0:
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole or index.column() != 0 or not str(value).strip():
            return False
        url, _ = self.entries[index.row()]
        self.entries[index.row()] = (url, str(value).strip())
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        self.changed.emit()
        return True

    def replace(self, entries, packages=None):
        entries = list(entries)
        packages = list(packages) if packages is not None else [''] * len(entries)
        if len(entries) != len(packages):
            raise ValueError('Package metadata must match the link count.')
        self.beginResetModel()
        self.entries = entries
        self.package_names = packages
        self.endResetModel()
        self.changed.emit()

    def add(self, entries, packages=None):
        entries = list(entries)
        packages = list(packages) if packages is not None else [''] * len(entries)
        if len(entries) != len(packages):
            raise ValueError('Package metadata must match the link count.')
        combined = list(zip(self.entries, self.package_names)) + list(zip(entries, packages))
        merged = list(dict.fromkeys(combined))
        added = len(merged) - len(self.entries)
        self.replace([entry for entry, _ in merged], [package for _, package in merged])
        return added


class PasteDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Add links')
        self.resize(720, 470)
        self.entries = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)
        layout.addWidget(label('Add links', 'heading'))
        layout.addWidget(label('Paste URLs from any host. Add a display name before each URL if you have one.', 'muted', True))
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText('Project archive.zip | https://example.com/archive.zip\nDocumentation.pdf | https://example.org/document.pdf\nhttps://example.net/another-file.zip')
        layout.addWidget(self.editor, 1)
        self.error = label('', 'muted', True)
        layout.addWidget(self.error)
        actions = QHBoxLayout()
        actions.addWidget(label('Exact duplicate entries are skipped.', 'muted'))
        actions.addStretch()
        actions.addWidget(button('Cancel', self.reject, subtle=True))
        actions.addWidget(button('Add to collection', self.apply, primary=True))
        layout.addLayout(actions)

    def apply(self):
        try:
            self.entries = core.parse_text(self.editor.toPlainText())
            self.accept()
        except Exception as error:
            self.error.setText(str(error))


def load_collection(paths, progress=lambda text: None):
    rows = []
    for path in paths:
        progress(f'Opening {Path(path).name}…')
        if Path(path).suffix.lower() == '.dlc':
            rows.extend(core.read_dlc(path))
        else:
            rows.extend(core.read_entries(path, include_packages=True))
    return rows


class ImportWorker(QThread):
    progress = Signal(str)
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, paths):
        super().__init__()
        self.paths = paths

    def run(self):
        try:
            self.completed.emit(load_collection(self.paths, self.progress.emit))
        except Exception as error:
            self.failed.emit(str(error))


class BuildWorker(QThread):
    progress = Signal(str)
    completed = Signal(str, int, bool)
    failed = Signal(str)

    def __init__(self, package, entries, destination, verify):
        super().__init__()
        self.package, self.entries, self.destination, self.verify = package, entries, destination, verify

    def run(self):
        try:
            core.create(self.package, self.entries, self.destination, self.verify, self.progress.emit)
            self.completed.emit(self.destination, len(self.entries), self.verify)
        except Exception as error:
            self.failed.emit(str(error))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LinkForge — Container Studio')
        self.setWindowIcon(QIcon(str(ASSETS / 'logo.ico')))
        self.resize(1320, 850)
        self.setMinimumSize(1080, 740)
        self.setAcceptDrops(True)
        self.dialog_dir = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
        self.output = None
        self.worker = None
        self.model = LinkModel()
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)
        self.layout_ui()
        self.model.changed.connect(self.refresh)
        self.table.selectionModel().selectionChanged.connect(self.selection_changed)
        self.refresh()
        for shortcut, callback in [('Ctrl+O', self.import_files), ('Ctrl+Shift+V', self.paste), ('Delete', self.remove_selected)]:
            key = QShortcut(QKeySequence(shortcut), self)
            if shortcut == 'Delete':
                key.setContext(Qt.WidgetWithChildrenShortcut)
                key.setParent(self.table)
            else:
                key.setContext(Qt.WindowShortcut)
            key.activated.connect(callback)

    def layout_ui(self):
        surface = QWidget()
        surface.setObjectName('surface')
        self.setCentralWidget(surface)
        outer = QHBoxLayout(surface)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(186)
        rail = QVBoxLayout(sidebar)
        rail.setContentsMargins(20, 28, 20, 22)
        rail.setSpacing(16)
        icon = QLabel()
        icon.setPixmap(QIcon(str(ASSETS / 'logo.png')).pixmap(48, 48))
        rail.addWidget(icon)
        rail.addWidget(label('LinkForge', 'brand'))
        rail.addWidget(label('CONTAINER STUDIO', 'eyebrow'))
        rail.addSpacing(25)
        nav = QPushButton('  Link collection')
        nav.setObjectName('nav')
        nav.setFocusPolicy(Qt.NoFocus)
        rail.addWidget(nav)
        rail.addWidget(button('Open DLC…', self.open_dlc, subtle=True))
        rail.addSpacing(4)
        rail.addWidget(label('WORKFLOW', 'eyebrow'))
        for title, description in [('01  Collect', 'Import links or open a DLC.'), ('02  Organize', 'Review names and packages.'), ('03  Export', 'Save as DLC, CSV, or TXT.')]:
            rail.addWidget(label(title))
            rail.addWidget(label(description, 'muted', True))
        rail.addStretch()
        rail.addWidget(label('HTTP / HTTPS', 'eyebrow'))
        rail.addWidget(label('Any host. One collection.', 'muted', True))
        rail.addWidget(label('Desktop  /  2.1.3', 'muted'))
        outer.addWidget(sidebar)
        main = QVBoxLayout()
        main.setContentsMargins(30, 22, 30, 20)
        main.setSpacing(14)
        outer.addLayout(main, 1)
        header = QHBoxLayout()
        intro = QVBoxLayout()
        intro.setSpacing(6)
        intro.addWidget(label('YOUR WORKSPACE', 'eyebrow'))
        intro.addWidget(label('Link collection', 'heading'))
        intro.addWidget(label('Compile named links—or extract a DLC into CSV or TXT.', 'muted', True))
        header.addLayout(intro, 1)
        header.addWidget(label('JDownloader compatible', 'badge'), 0, Qt.AlignTop)
        main.addLayout(header)
        stats = QHBoxLayout()
        stats.setSpacing(14)
        self.stat_values = []
        for title, note in [('TOTAL LINKS', 'in your collection'), ('SOURCE HOSTS', 'mixed hosts supported'), ('CUSTOM NAMES', 'labels ready for export')]:
            frame, column = card()
            column.setContentsMargins(18, 10, 18, 10)
            column.setSpacing(1)
            column.addWidget(label(title, 'eyebrow'))
            value = label('0', 'value')
            self.stat_values.append(value)
            column.addWidget(value)
            column.addWidget(label(note, 'muted'))
            stats.addWidget(frame, 1)
        main.addLayout(stats)
        workspace = QHBoxLayout()
        workspace.setSpacing(18)
        left, collection = card()
        collection.setContentsMargins(0, 0, 0, 0)
        collection.setSpacing(0)
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(16, 14, 16, 12)
        toolbar.setSpacing(8)
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search names, hosts, or URLs…')
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.filter_links)
        toolbar.addWidget(self.search, 1)
        self.import_button = button('Import', self.import_files)
        self.import_button.setToolTip('Open DLC containers or import CSV/TXT • Ctrl+O')
        toolbar.addWidget(self.import_button)
        self.paste_button = button('+ Add links', self.paste, primary=True)
        toolbar.addWidget(self.paste_button)
        collection.addLayout(toolbar)
        self.pages = QStackedWidget()
        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.clicked.connect(self.open_clicked_link)
        self.table.setMouseTracking(True)
        self.table.entered.connect(lambda index: self.table.viewport().setCursor(Qt.PointingHandCursor if index.column() == 3 else Qt.ArrowCursor))
        self.table.viewportEntered.connect(lambda: self.table.viewport().unsetCursor())
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.link_menu)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(-1, Qt.AscendingOrder)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.horizontalHeader().setMinimumSectionSize(90)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.table.setColumnWidth(1, 145)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 210)
        self.table.setWordWrap(False)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.pages.addWidget(self.table)
        empty = QWidget()
        empty_layout = QVBoxLayout(empty)
        empty_layout.setContentsMargins(36, 20, 36, 20)
        empty_layout.setSpacing(12)
        empty_layout.addStretch()
        illustration = QLabel()
        illustration.setPixmap(QIcon(str(ASSETS / 'logo.png')).pixmap(76, 76))
        illustration.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(illustration)
        self.empty_title = label('Your next collection starts here', 'section')
        self.empty_title.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(self.empty_title)
        self.empty_hint = label('Drop DLC, CSV, or TXT files here,\nor paste links from any host.', 'muted', True)
        self.empty_hint.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(self.empty_hint)
        empty_layout.addStretch()
        self.pages.addWidget(empty)
        collection.addWidget(self.pages, 1)
        footer = QHBoxLayout()
        footer.setContentsMargins(16, 10, 16, 12)
        self.visible_count = label('No links yet', 'muted')
        footer.addWidget(self.visible_count, 1)
        self.remove_button = button('Remove', self.remove_selected, subtle=True)
        self.clear_button = button('Clear', self.clear_all, subtle=True)
        footer.addWidget(self.remove_button)
        footer.addWidget(self.clear_button)
        collection.addLayout(footer)
        workspace.addWidget(left, 1)
        self.settings, settings = card()
        self.settings.setFixedWidth(300)
        settings.setSpacing(10)
        settings.addWidget(label('Package settings', 'section'))
        settings.addWidget(label('PACKAGE NAME', 'eyebrow'))
        self.package = QLineEdit('My collection')
        self.package.setMinimumHeight(40)
        self.package.setPlaceholderText('Give your package a name')
        settings.addWidget(self.package)
        self.package.setToolTip('Shown as the package title in JDownloader’s LinkGrabber.')
        settings.addWidget(label('FILE NAMING', 'eyebrow'))
        self.extension = QComboBox()
        self.extension.setMinimumHeight(40)
        self.extension.addItems(['Keep original names', 'Append .rar if missing'])
        settings.addWidget(self.extension)
        self.extension.setToolTip('Display names only. Original source URLs stay unchanged.')
        self.verify = QCheckBox('Verify container before saving')
        self.verify.setChecked(True)
        settings.addWidget(self.verify)
        settings.addWidget(label('Compares every URL and filename\nusing JDownloader’s key service.', 'muted', True))
        settings.addStretch(1)
        self.notice = label('Internet connection required.\nNo files are downloaded by this app.', 'notice', True)
        self.notice.setMinimumHeight(56)
        settings.addWidget(self.notice)
        self.create_button = button('Create DLC package', self.build, primary=True)
        self.create_button.setMinimumHeight(44)
        settings.addWidget(self.create_button)
        self.export_button = QPushButton('Export CSV / TXT')
        self.export_button.setCursor(Qt.PointingHandCursor)
        export_menu = QMenu(self.export_button)
        export_menu.addAction('CSV — names, packages, and URLs', lambda: self.export_list('csv'))
        export_menu.addAction('TXT — URLs, one per line', lambda: self.export_list('txt'))
        self.export_button.setMenu(export_menu)
        settings.addWidget(self.export_button)
        self.open_button = button('Open output folder', self.open_output, subtle=True)
        self.open_button.hide()
        settings.addWidget(self.open_button)
        workspace.addWidget(self.settings)
        main.addLayout(workspace, 1)
        main.addWidget(label('Click a URL to open it. Right-click for copy options. Double-click a name to edit. Exports preserve original URLs.', 'muted', True))
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.hide()
        main.addWidget(self.progress)
        self.statusBar().showMessage('Ready to create a collection')
        self.statusBar().addPermanentWidget(label('DLC  •  Encrypted link container', 'muted'))

    def filter_links(self, text):
        self.proxy.setFilterFixedString(text)
        self.update_visible()

    def update_visible(self):
        total, visible = len(self.model.entries), self.proxy.rowCount()
        self.visible_count.setText(f'{visible:,} of {total:,} links' if total else 'No links yet')
        self.pages.setCurrentIndex(0 if visible else 1)
        self.empty_title.setText('No matching links' if total else 'Your next collection starts here')
        self.empty_hint.setText('Try another search. Your full collection is still included in the DLC.' if total else 'Drop DLC, CSV, or TXT files here,\nor paste links from any host.')

    def refresh(self):
        entries = self.model.entries
        values = [len(entries), len({core.urlsplit(u).hostname for u, _ in entries}), sum(n != u for u, n in entries)]
        for widget, value in zip(self.stat_values, values):
            widget.setText(f'{value:,}')
        busy = bool(self.worker and self.worker.isRunning())
        self.create_button.setEnabled(bool(entries) and not busy)
        self.export_button.setEnabled(bool(entries) and not busy)
        self.clear_button.setEnabled(bool(entries) and not busy)
        self.update_visible()
        self.selection_changed()

    def selection_changed(self, *_):
        self.remove_button.setEnabled(bool(self.table.selectionModel().selectedRows()) and not self.is_busy())

    def is_busy(self):
        return bool(self.worker and self.worker.isRunning())

    def initial_directory(self):
        return str(self.dialog_dir if self.dialog_dir.is_dir() else Path(sys.executable).resolve().parent)

    def remember(self, path):
        folder = Path(path).resolve().parent
        if folder.is_dir():
            self.dialog_dir = folder

    def open_dlc(self):
        self.import_files(dlc_only=True)

    def import_files(self, dlc_only=False):
        if self.is_busy():
            return
        filters = 'DLC containers (*.dlc)' if dlc_only else 'Containers and lists (*.dlc *.csv *.txt);;DLC containers (*.dlc);;Link lists (*.csv *.txt)'
        paths, _ = QFileDialog.getOpenFileNames(self, 'Open DLC or import links', self.initial_directory(),
            filters, options=QFileDialog.DontUseNativeDialog)
        if paths:
            self.import_paths(paths)

    def apply_import(self, rows, paths):
        was_empty = not self.model.entries
        added = self.model.add([(row['url'], row['name']) for row in rows], [row.get('package', '') for row in rows])
        packages = {row.get('package', '') for row in rows} - {''}
        if was_empty and len(packages) == 1:
            self.package.setText(next(iter(packages)))
        self.remember(paths[-1])
        self.statusBar().showMessage(f'Loaded {added:,} links • {len(packages):,} source packages • Export CSV or TXT to extract them')

    def import_failed(self, error):
        self.statusBar().showMessage('Import failed. Your collection has not been changed.')
        QMessageBox.warning(self, 'Could not open container or list', error)

    def import_paths(self, paths):
        if self.is_busy() or not paths:
            return
        if any(Path(path).suffix.lower() == '.dlc' for path in paths):
            self.worker = ImportWorker(paths)
            self.worker.progress.connect(self.statusBar().showMessage)
            self.worker.completed.connect(lambda rows: self.apply_import(rows, paths))
            self.worker.failed.connect(self.import_failed)
            self.worker.finished.connect(lambda: self.set_busy(False))
            self.set_busy(True)
            self.worker.start()
        else:
            try:
                self.apply_import(load_collection(paths), paths)
            except Exception as error:
                self.import_failed(str(error))

    def paste(self):
        if self.is_busy():
            return
        dialog = PasteDialog(self)
        if dialog.exec() == QDialog.Accepted:
            added = self.model.add(dialog.entries)
            self.statusBar().showMessage(f'Added {added:,} links to the collection')

    def open_row_link(self, row):
        if self.is_busy() or not 0 <= row < len(self.model.entries):
            return
        original = self.model.entries[row][0]
        target = QUrl.fromEncoded(original.encode('utf-8'), QUrl.TolerantMode)
        if not target.isValid() or target.scheme().lower() not in ('http', 'https') or not target.host() or target.userInfo():
            self.statusBar().showMessage('Only HTTP/HTTPS web links can be opened. Use Copy link to inspect this value.')
            return
        # Do not unquote or re-encode the stored URL before handing it to Qt.
        if QDesktopServices.openUrl(target):
            self.statusBar().showMessage('Opened in your default browser. Host logins and restrictions still apply.')
        else:
            self.statusBar().showMessage('Could not open your browser. Right-click the row and choose Copy link.')

    def open_clicked_link(self, index):
        if index.isValid() and index.column() == 3:
            self.open_row_link(self.proxy.mapToSource(index).row())

    def copy_row_link(self, row):
        if 0 <= row < len(self.model.entries):
            QApplication.clipboard().setText(self.model.entries[row][0])
            self.statusBar().showMessage('Original URL copied. URL encoding has been preserved.')

    def copy_selected_links(self):
        indexes = sorted(self.table.selectionModel().selectedRows(), key=lambda index: index.row())
        links = [self.model.entries[self.proxy.mapToSource(index).row()][0] for index in indexes]
        if links:
            QApplication.clipboard().setText('\n'.join(links))
            self.statusBar().showMessage(f'Copied {len(links):,} original links')

    def link_menu(self, point):
        index = self.table.indexAt(point)
        if not index.isValid() or self.is_busy():
            return
        if not self.table.selectionModel().isRowSelected(index.row(), QModelIndex()):
            self.table.selectRow(index.row())
        row = self.proxy.mapToSource(index).row()
        menu = QMenu(self.table)
        menu.addAction('Open link in browser', lambda: self.open_row_link(row))
        menu.addAction('Copy link', lambda: self.copy_row_link(row))
        if len(self.table.selectionModel().selectedRows()) > 1:
            menu.addAction('Copy selected links', self.copy_selected_links)
        menu.exec(self.table.viewport().mapToGlobal(point))

    def remove_selected(self):
        if self.is_busy() or self.table.state() == QAbstractItemView.EditingState:
            return
        rows = {self.proxy.mapToSource(index).row() for index in self.table.selectionModel().selectedRows()}
        if rows:
            self.model.replace([entry for i, entry in enumerate(self.model.entries) if i not in rows],
                               [name for i, name in enumerate(self.model.package_names) if i not in rows])
            self.statusBar().showMessage(f'Removed {len(rows):,} links')

    def clear_all(self):
        if self.is_busy():
            return
        if QMessageBox.question(self, 'Clear collection?', 'Remove every link from this collection? Original source files will not be changed.',
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.model.replace([])
            self.search.clear()
            self.statusBar().showMessage('Collection cleared')

    def selected_entries(self):
        # Search changes the view only, never the set of exported links.
        entries = list(self.model.entries)
        if self.extension.currentIndex() == 1:
            entries = [(u, n if n.lower().endswith('.rar') else n + '.rar') for u, n in entries]
        return entries

    def make_save_dialog(self, title, filename, suffix, file_filter):
        # Apply the suffix BEFORE Qt checks overwrite confirmation.
        dialog = QFileDialog(self, title, self.initial_directory(), file_filter)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setOption(QFileDialog.DontConfirmOverwrite, False)
        dialog.setDefaultSuffix(suffix)
        dialog.selectFile(filename)
        return dialog

    def choose_output(self, title, filename, suffix, file_filter):
        dialog = self.make_save_dialog(title, filename, suffix, file_filter)
        if dialog.exec() == QDialog.Accepted:
            return dialog.selectedFiles()[0]
        return ''

    def export_list(self, kind='csv'):
        if not self.model.entries or self.is_busy():
            return
        description = 'CSV — names, packages, and URLs' if kind == 'csv' else 'TXT — URLs only'
        path = self.choose_output('Export ' + description, 'Link_collection.' + kind, kind,
                                  ('CSV link list (*.csv)' if kind == 'csv' else 'Text link list (*.txt)'))
        if not path:
            return
        try:
            rows = [{'url': url, 'name': name, 'package': package} for (url, name), package
                    in zip(self.selected_entries(), self.model.package_names)]
            core.export_collection(rows, path, kind)
            self.remember(path)
            self.output = path
            self.open_button.show()
            self.statusBar().showMessage(f'Exported {len(rows):,} links to {Path(path).name}')
        except Exception as error:
            QMessageBox.warning(self, 'Export failed', str(error))

    def build(self):
        if self.is_busy() or not self.model.entries:
            return
        package = self.package.text().strip()
        if not package:
            self.package.setFocus()
            self.statusBar().showMessage('Enter a package name before creating a DLC.')
            return
        path = self.choose_output('Create DLC package', 'Link_collection.dlc', 'dlc', 'JDownloader container (*.dlc)')
        if not path:
            return
        self.remember(path)
        self.worker = BuildWorker(package, self.selected_entries(), path, self.verify.isChecked())
        self.worker.progress.connect(self.statusBar().showMessage)
        self.worker.completed.connect(self.build_complete)
        self.worker.failed.connect(self.build_failed)
        self.worker.finished.connect(lambda: self.set_busy(False))
        self.set_busy(True)
        self.worker.start()

    def set_busy(self, busy):
        self.import_button.setEnabled(not busy)
        self.paste_button.setEnabled(not busy)
        self.settings.setEnabled(not busy)
        self.table.setEnabled(not busy)
        self.clear_button.setEnabled(not busy and bool(self.model.entries))
        self.remove_button.setEnabled(not busy and bool(self.table.selectionModel().selectedRows()))
        self.progress.setVisible(busy)
        self.progress.setRange(0, 0 if busy else 100)
        if not busy:
            self.refresh()

    def build_complete(self, path, count, verified):
        self.output = path
        self.open_button.show()
        self.statusBar().showMessage(f'Package ready • {count:,} links • {"Verified" if verified else "Verification skipped"} • {Path(path).name}')

    def build_failed(self, error):
        self.statusBar().showMessage('Package creation failed. No new container was saved.')
        QMessageBox.warning(self, 'Could not create package', error)

    def open_output(self):
        if self.output:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.output).resolve().parent)))

    def dragEnterEvent(self, event):
        if not self.is_busy() and event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and all(u.isLocalFile() and Path(u.toLocalFile()).suffix.lower() in ('.dlc', '.csv', '.txt') for u in urls):
                event.acceptProposedAction()

    def dropEvent(self, event):
        self.import_paths([url.toLocalFile() for url in event.mimeData().urls()])
        event.acceptProposedAction()

    def closeEvent(self, event):
        if self.is_busy():
            QMessageBox.information(self, 'Operation in progress', 'Please let the current container operation finish before closing LinkForge.')
            event.ignore()
        else:
            event.accept()


def run():
    app = QApplication(sys.argv)
    # Use the same Windows font family throughout the interface.
    fonts = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    for name in ('segoeui.ttf', 'segoeuib.ttf'):
        if (fonts / name).is_file():
            QFontDatabase.addApplicationFont(str(fonts / name))
    app.setStyle('Fusion')
    app.setStyleSheet(STYLE.replace('CHECK_PATH', (ASSETS / 'check.png').as_posix()).replace('CHEVRON_PATH', (ASSETS / 'chevron.png').as_posix()))
    app.setApplicationName('LinkForge')
    app.setWindowIcon(QIcon(str(ASSETS / 'logo.ico')))
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(run())
