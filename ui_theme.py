"""LinkForge 2 desktop design tokens and Qt styling."""
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
