"""QSS themes — realistic PySide6 styling (no HTML mockups)."""

from shared_layout import LayoutStyle, SampleMeta

# Shared widget rules appended to each theme
_BASE_WIDGETS = """
QScrollArea { background: transparent; border: none; }
QScrollArea > QWidget > QWidget { background: transparent; }
QTableWidget { background: palette(base); alternate-background-color: transparent; }
QHeaderView::section {
    background: transparent;
    border: none;
    padding: 6px 4px;
    font-weight: 600;
}
QToolButton#clearKey {
    border: none;
    padding: 2px 6px;
    color: #6e6e73;
}
QPushButton#linkButton {
    text-align: left;
    padding: 0;
    border: none;
    font-size: 9pt;
}
QPushButton#dangerIcon {
    padding: 0;
    min-width: 24px;
    max-width: 28px;
}
"""


def theme_1_bright_port() -> tuple[SampleMeta, str]:
    """Closest Qt equivalent to current Tk Theme 1 (flat, Apple-like light)."""
    meta = SampleMeta(
        1,
        "Bright minimal (Tk port)",
        "Same layout as v2.0.0; flat QPushButton replaces PIL gradients.",
        LayoutStyle.CLASSIC,
    )
    qss = """
    QWidget { background-color: #ffffff; color: #1d1d1f; }
    QFrame#header { background-color: #f5f5f7; border-bottom: 1px solid #d2d2d7; }
    QLabel#appTitle { font-family: Georgia; font-size: 15pt; font-weight: bold; }
    QGroupBox {
        font-weight: 600;
        border: 1px solid #d2d2d7;
        border-radius: 6px;
        margin-top: 10px;
        padding: 12px 10px 10px 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
        color: #0066cc;
    }
    QLineEdit, QComboBox {
        border: 1px solid #d2d2d7;
        border-radius: 4px;
        padding: 5px 8px;
        background: #ffffff;
    }
    QLineEdit:focus, QComboBox:focus { border-color: #0066cc; }
    QPushButton#primary, QPushButton#headerAction {
        background-color: #0066cc;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        padding: 6px 14px;
        font-weight: 600;
    }
    QPushButton#primary:hover, QPushButton#headerAction:hover { background-color: #0077e6; }
    QPushButton#primary:pressed, QPushButton#headerAction:pressed { background-color: #004c99; }
    QPushButton#secondary {
        background-color: #f5f5f7;
        color: #1d1d1f;
        border: 1px solid #d2d2d7;
        border-radius: 5px;
        padding: 6px 12px;
    }
    QPushButton#secondary:hover { background-color: #ebebef; }
    QPushButton#linkButton { color: #0066cc; }
    QCheckBox#autostart { color: #ff3b30; font-weight: 500; }
    QTableWidget { border: 1px solid #ebebef; border-radius: 4px; }
    QPushButton#dangerIcon { color: #ff3b30; border: 1px solid transparent; background: transparent; }
    QPushButton#dangerIcon:hover { background: #fff0ef; border-radius: 4px; }
    """ + _BASE_WIDGETS
    return meta, qss


def theme_2_windows_fluent() -> tuple[SampleMeta, str]:
    """Windows 11–style accent, softer corners, Mica-like header."""
    meta = SampleMeta(
        2,
        "Windows Fluent",
        "Accent #0078D4; larger padding; subtle control fills.",
        LayoutStyle.CLASSIC,
    )
    qss = """
    QWidget { background-color: #f3f3f3; color: #202020; }
    QFrame#header {
        background-color: #fafafa;
        border-bottom: 1px solid #e5e5e5;
    }
    QLabel#appTitle { font-size: 14pt; font-weight: 600; }
    QGroupBox {
        font-weight: 600;
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        margin-top: 12px;
        padding: 14px;
    }
    QGroupBox::title { color: #0078D4; left: 12px; padding: 0 6px; }
    QLineEdit, QComboBox {
        background: #f9f9f9;
        border: 1px solid #d1d1d1;
        border-bottom: 2px solid #d1d1d1;
        border-radius: 4px;
        padding: 6px 10px;
        min-height: 20px;
    }
    QLineEdit:focus, QComboBox:focus { border-bottom-color: #0078D4; background: #ffffff; }
    QPushButton#primary, QPushButton#headerAction {
        background-color: #0078D4;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 7px 16px;
    }
    QPushButton#primary:hover, QPushButton#headerAction:hover { background-color: #106EBE; }
    QPushButton#secondary {
        background: #ffffff;
        border: 1px solid #d1d1d1;
        border-radius: 4px;
        padding: 7px 14px;
    }
    QPushButton#linkButton { color: #0078D4; }
    QCheckBox#autostart { color: #c50f1f; }
    QTableWidget { background: #ffffff; border-radius: 6px; border: 1px solid #e5e5e5; }
    QHeaderView::section { background: #f5f5f5; border-bottom: 1px solid #e5e5e5; }
    """ + _BASE_WIDGETS
    return meta, qss


def theme_3_dark_dev() -> tuple[SampleMeta, str]:
    """Dark surfaces — common for Qt apps with custom QSS."""
    meta = SampleMeta(
        3,
        "Dark (developer)",
        "Low glare; green accent for primary actions.",
        LayoutStyle.CLASSIC,
    )
    qss = """
    QWidget { background-color: #1e1e1e; color: #e0e0e0; }
    QFrame#header { background-color: #252526; border-bottom: 1px solid #3c3c3c; }
    QLabel#appTitle { font-size: 14pt; font-weight: 600; color: #ffffff; }
    QGroupBox {
        border: 1px solid #3c3c3c;
        border-radius: 6px;
        margin-top: 10px;
        padding: 12px;
        background: #252526;
    }
    QGroupBox::title { color: #4ec9b0; left: 10px; }
    QLineEdit, QComboBox {
        background: #1e1e1e;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
        padding: 5px 8px;
        color: #e0e0e0;
    }
    QLineEdit:focus, QComboBox:focus { border-color: #4ec9b0; }
    QComboBox QAbstractItemView { background: #252526; color: #e0e0e0; selection-background-color: #094771; }
    QPushButton#primary, QPushButton#headerAction {
        background-color: #0e639c;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 6px 14px;
    }
    QPushButton#primary:hover, QPushButton#headerAction:hover { background-color: #1177bb; }
    QPushButton#secondary {
        background: #2d2d30;
        border: 1px solid #3c3c3c;
        border-radius: 4px;
        padding: 6px 12px;
        color: #e0e0e0;
    }
    QPushButton#linkButton { color: #4fc1ff; }
    QCheckBox#autostart { color: #f48771; }
    QTableWidget {
        background-color: #1e1e1e;
        alternate-background-color: #252526;
        color: #e0e0e0;
        gridline-color: #3c3c3c;
        border: 1px solid #3c3c3c;
    }
    QTableWidget::item { background-color: #1e1e1e; padding: 4px; }
    QTableWidget::item:alternate { background-color: #252526; }
    QHeaderView::section { color: #cccccc; background: #2d2d30; border: none; }
    QScrollArea { background: #1e1e1e; }
    QPushButton#dangerIcon { color: #f48771; background: transparent; border: none; }
    """ + _BASE_WIDGETS
    return meta, qss


def theme_4_sidebar() -> tuple[SampleMeta, str]:
    meta = SampleMeta(
        4,
        "Sidebar navigation",
        "Sections in QStackedWidget; less vertical scroll.",
        LayoutStyle.SIDEBAR,
    )
    qss = """
    QWidget { background: #ffffff; color: #1d1d1f; }
    QFrame#header { background: #f5f5f7; border-bottom: 1px solid #d2d2d7; }
    QLabel#appTitle { font-size: 14pt; font-weight: 700; }
    QListWidget#sideNav {
        background: #f5f5f7;
        border: none;
        border-right: 1px solid #d2d2d7;
        padding: 8px 0;
        outline: none;
    }
    QListWidget#sideNav::item {
        padding: 10px 14px;
        margin: 2px 8px;
        border-radius: 6px;
    }
    QListWidget#sideNav::item:selected {
        background: #0066cc;
        color: white;
    }
    QGroupBox {
        border: 1px solid #e0e0e5;
        border-radius: 8px;
        margin-top: 8px;
        padding: 12px;
        font-weight: 600;
    }
    QGroupBox::title { color: #0066cc; }
    QPushButton#primary, QPushButton#headerAction {
        background: #0066cc; color: white; border: none; border-radius: 5px; padding: 6px 14px;
    }
    QPushButton#secondary {
        background: #f5f5f7; border: 1px solid #d2d2d7; border-radius: 5px; padding: 6px 12px;
    }
    QLineEdit, QComboBox { border: 1px solid #d2d2d7; border-radius: 4px; padding: 5px 8px; }
    QCheckBox#autostart { color: #ff3b30; }
    """ + _BASE_WIDGETS
    return meta, qss


def theme_5_compact_toolbar() -> tuple[SampleMeta, str]:
    meta = SampleMeta(
        5,
        "Compact + action bar",
        "Segmented section jump; API actions on one row.",
        LayoutStyle.COMPACT_HEADER,
    )
    qss = """
    QWidget { background: #fafafa; color: #1d1d1f; }
    QFrame#header { background: #ffffff; border-bottom: 1px solid #e8e8ed; }
    QFrame#subToolbar { background: #f0f0f5; border-bottom: 1px solid #e0e0e5; }
    QLabel#appTitle { font-size: 13pt; font-weight: 600; }
    QPushButton#segment {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 14px;
        padding: 5px 12px;
        color: #6e6e73;
    }
    QPushButton#segment:checked {
        background: #ffffff;
        border-color: #d2d2d7;
        color: #1d1d1f;
        font-weight: 600;
    }
    QGroupBox {
        background: #ffffff;
        border: 1px solid #e8e8ed;
        border-radius: 10px;
        padding: 12px;
        margin-top: 10px;
    }
    QGroupBox::title { color: #5856d6; }
    QPushButton#primary {
        background: #5856d6; color: white; border: none; border-radius: 6px; padding: 7px 18px;
    }
    QPushButton#headerAction {
        background: #e8e8ed; color: #1d1d1f; border: none; border-radius: 6px; padding: 6px 12px;
    }
    QPushButton#headerAction:hover { background: #dcdce2; }
    QPushButton#secondary {
        background: #f5f5f7; border: 1px solid #d2d2d7; border-radius: 6px; padding: 6px 12px;
    }
    QPushButton#linkButton { color: #5856d6; }
    QCheckBox#autostart { color: #ff3b30; }
    QLineEdit, QComboBox { border: 1px solid #d2d2d7; border-radius: 6px; padding: 6px 8px; background: #fff; }
    """ + _BASE_WIDGETS
    return meta, qss


ALL_THEMES = [
    theme_1_bright_port,
    theme_2_windows_fluent,
    theme_3_dark_dev,
    theme_4_sidebar,
    theme_5_compact_toolbar,
]
