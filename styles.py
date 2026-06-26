"""
styles.py
Centralized QSS stylesheet + color palette for MedCore HMS.
A calm clinical blue/teal palette, generous spacing, rounded corners.
"""

PALETTE = {
    "bg": "#f4f7fa",
    "surface": "#ffffff",
    "sidebar": "#0b3954",
    "sidebar_active": "#0f4c75",
    "primary": "#0f4c75",
    "primary_dark": "#0b3954",
    "accent": "#3da5d9",
    "success": "#1e8e5a",
    "warning": "#c97a1f",
    "danger": "#c0392b",
    "text": "#1c2b36",
    "text_muted": "#5b6b76",
    "border": "#dfe6ec",
}

FONT_FAMILY = '"Segoe UI", "Helvetica Neue", Arial, sans-serif'

APP_QSS = f"""
* {{
    font-family: {FONT_FAMILY};
}}

QWidget {{
    background: {PALETTE["bg"]};
    color: {PALETTE["text"]};
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background: {PALETTE["bg"]};
}}

/* ---------- Sidebar ---------- */
#Sidebar {{
    background: {PALETTE["sidebar"]};
    min-width: 220px;
    max-width: 220px;
}}
#SidebarTitle {{
    color: white;
    font-size: 17px;
    font-weight: 700;
    padding: 22px 18px 4px 18px;
}}
#SidebarSubtitle {{
    color: #9fb8cc;
    font-size: 11px;
    padding: 0px 18px 18px 18px;
}}
QPushButton#NavButton {{
    background: transparent;
    color: #d6e6f2;
    text-align: left;
    padding: 12px 20px;
    border: none;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton#NavButton:hover {{
    background: {PALETTE["sidebar_active"]};
    color: white;
}}
QPushButton#NavButton:checked {{
    background: {PALETTE["accent"]};
    color: white;
    font-weight: 700;
}}
QPushButton#NavLogout {{
    background: transparent;
    color: #f3b9b9;
    text-align: left;
    padding: 12px 20px;
    border: none;
    font-size: 13px;
}}
QPushButton#NavLogout:hover {{
    background: {PALETTE["danger"]};
    color: white;
}}

/* ---------- Top bar ---------- */
#TopBar {{
    background: {PALETTE["surface"]};
    border-bottom: 1px solid {PALETTE["border"]};
}}
#TopBarTitle {{
    font-size: 19px;
    font-weight: 700;
    color: {PALETTE["text"]};
}}
#TopBarUser {{
    color: {PALETTE["text_muted"]};
    font-size: 12px;
}}

/* ---------- Cards ---------- */
.Card, QFrame#Card {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["border"]};
    border-radius: 10px;
}}
QFrame#StatCard {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["border"]};
    border-radius: 10px;
}}
QLabel#StatValue {{
    font-size: 26px;
    font-weight: 800;
    color: {PALETTE["primary_dark"]};
}}
QLabel#StatLabel {{
    color: {PALETTE["text_muted"]};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
}}

/* ---------- Headings ---------- */
QLabel#PageTitle {{
    font-size: 20px;
    font-weight: 800;
    color: {PALETTE["text"]};
}}
QLabel#SectionTitle {{
    font-size: 15px;
    font-weight: 700;
    color: {PALETTE["primary_dark"]};
}}
QLabel#Muted {{
    color: {PALETTE["text_muted"]};
}}

/* ---------- Inputs ---------- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit, QPlainTextEdit {{
    background: white;
    color: {PALETTE["text"]};
    border: 1px solid {PALETTE["border"]};
    padding: 7px 9px;
    border-radius: 6px;
    selection-background-color: {PALETTE["accent"]};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus {{
    border: 1px solid {PALETTE["accent"]};
}}
QComboBox::drop-down {{ border: none; width: 24px; }}
QLabel {{ color: {PALETTE["text"]}; }}

/* ---------- Buttons ---------- */
QPushButton {{
    background: {PALETTE["primary"]};
    color: white;
    border: none;
    padding: 9px 16px;
    border-radius: 6px;
    font-weight: 600;
}}
QPushButton:hover {{ background: {PALETTE["primary_dark"]}; }}
QPushButton:disabled {{ background: #aebcc6; color: #eef2f5; }}

QPushButton#SecondaryButton {{
    background: white;
    color: {PALETTE["primary"]};
    border: 1px solid {PALETTE["primary"]};
}}
QPushButton#SecondaryButton:hover {{ background: #eaf3fa; }}

QPushButton#DangerButton {{ background: {PALETTE["danger"]}; }}
QPushButton#DangerButton:hover {{ background: #962d22; }}

QPushButton#SuccessButton {{ background: {PALETTE["success"]}; }}
QPushButton#SuccessButton:hover {{ background: #15693f; }}

/* ---------- Tables ---------- */
QTableWidget {{
    background: white;
    border: 1px solid {PALETTE["border"]};
    border-radius: 8px;
    gridline-color: {PALETTE["border"]};
    selection-background-color: #d8ecf9;
    selection-color: {PALETTE["text"]};
}}
QHeaderView::section {{
    background: #eef3f7;
    color: {PALETTE["text_muted"]};
    padding: 8px;
    border: none;
    border-bottom: 1px solid {PALETTE["border"]};
    font-weight: 700;
    font-size: 11px;
}}
QTableWidget::item {{ padding: 6px; }}

/* ---------- Tabs ---------- */
QTabWidget::pane {{ border: 1px solid {PALETTE["border"]}; border-radius: 8px; background: white; }}
QTabBar::tab {{
    background: transparent;
    color: {PALETTE["text_muted"]};
    padding: 9px 16px;
    font-weight: 600;
}}
QTabBar::tab:selected {{ color: {PALETTE["primary"]}; border-bottom: 2px solid {PALETTE["primary"]}; }}

/* ---------- Scrollbars ---------- */
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: #c3d2db; border-radius: 5px; min-height: 24px; }}
QScrollBar::handle:vertical:hover {{ background: #9db2bf; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; }}
QScrollBar::handle:horizontal {{ background: #c3d2db; border-radius: 5px; }}

/* ---------- Misc ---------- */
QMessageBox {{ background: {PALETTE["surface"]}; }}
QToolTip {{
    background: {PALETTE["primary_dark"]};
    color: white;
    border: none;
    padding: 6px;
    border-radius: 4px;
}}
"""

LOGIN_QSS = f"""
#LoginRoot {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 {PALETTE["sidebar"]}, stop:1 {PALETTE["primary"]}); }}
#LoginCard {{ background: white; border-radius: 14px; }}
#LoginCard QLabel  {{ color: {PALETTE["text"]}; }}
#LoginCard QLineEdit  {{ color: {PALETTE["text"]}; background: white;
    border: 1px solid {PALETTE["border"]}; padding: 7px 9px; border-radius: 6px; }}
#LoginCard QLineEdit:focus {{ border: 1px solid {PALETTE["accent"]}; }}
#LoginCard QComboBox  {{ color: {PALETTE["text"]}; background: white;
    border: 1px solid {PALETTE["border"]}; padding: 7px 9px; border-radius: 6px; }}
#LoginCard QSpinBox   {{ color: {PALETTE["text"]}; background: white;
    border: 1px solid {PALETTE["border"]}; padding: 7px 9px; border-radius: 6px; }}
#LoginCard QDateEdit  {{ color: {PALETTE["text"]}; background: white;
    border: 1px solid {PALETTE["border"]}; padding: 7px 9px; border-radius: 6px; }}
#LoginCard QTextEdit  {{ color: {PALETTE["text"]}; background: white;
    border: 1px solid {PALETTE["border"]}; padding: 7px 9px; border-radius: 6px; }}
#LoginCard QTabWidget::pane {{ border: 1px solid {PALETTE["border"]}; border-radius: 6px; background: white; }}
#LoginCard QTabBar::tab {{ color: {PALETTE["text_muted"]}; background: transparent;
    padding: 8px 14px; font-weight: 600; }}
#LoginCard QTabBar::tab:selected {{ color: {PALETTE["primary"]};
    border-bottom: 2px solid {PALETTE["primary"]}; }}
#LoginCard QPushButton {{ background: {PALETTE["primary"]}; color: white;
    border: none; padding: 9px 16px; border-radius: 6px; font-weight: 600; }}
#LoginCard QPushButton:hover {{ background: {PALETTE["primary_dark"]}; }}
#LoginCard QScrollArea {{ background: transparent; border: none; }}
#LoginCard QScrollArea > QWidget > QWidget {{ background: transparent; }}
#LoginTitle {{ font-size: 22px; font-weight: 800; color: {PALETTE["primary_dark"]}; }}
#LoginSubtitle {{ color: {PALETTE["text_muted"]}; font-size: 12px; }}
#BrandTitle {{ color: white; font-size: 30px; font-weight: 800; }}
#BrandSubtitle {{ color: #cfe4f2; font-size: 13px; }}
#BrandTagline {{ color: #9fcbe6; font-size: 12px; }}
"""
