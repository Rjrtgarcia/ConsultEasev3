#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - UI Styles Module

This module defines consistent UI styling for the application.
"""

# Card styles
CARD_STYLE = """
    QFrame {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
    }
"""

# Label styles
TITLE_LABEL_STYLE = """
    QLabel {
        font-family: 'Segoe UI', Arial;
        font-size: 16px;
        font-weight: bold;
        color: #333333;
    }
"""

SUBTITLE_LABEL_STYLE = """
    QLabel {
        font-family: 'Segoe UI', Arial;
        font-size: 14px;
        color: #555555;
    }
"""

INFO_LABEL_STYLE = """
    QLabel {
        font-family: 'Segoe UI', Arial;
        font-size: 12px;
        color: #666666;
    }
"""

# Status label styles
STATUS_LABEL_STYLES = {
    "active": """
        QLabel {
            background-color: #4CAF50;
            color: white;
            font-family: 'Segoe UI', Arial;
            font-size: 12px;
            font-weight: bold;
            border-radius: 4px;
            padding: 3px 8px;
        }
    """,
    "inactive": """
        QLabel {
            background-color: #F44336;
            color: white;
            font-family: 'Segoe UI', Arial;
            font-size: 12px;
            font-weight: bold;
            border-radius: 4px;
            padding: 3px 8px;
        }
    """,
    "maintenance": """
        QLabel {
            background-color: #FF9800;
            color: white;
            font-family: 'Segoe UI', Arial;
            font-size: 12px;
            font-weight: bold;
            border-radius: 4px;
            padding: 3px 8px;
        }
    """
}

# Button styles
ACTION_BUTTON_STYLE = """
    QPushButton {
        background-color: #2196F3;
        color: white;
        font-family: 'Segoe UI', Arial;
        font-size: 12px;
        font-weight: bold;
        border-radius: 4px;
        padding: 5px 10px;
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: #1976D2;
    }
    QPushButton:pressed {
        background-color: #0D47A1;
    }
"""

# Form styles
FORM_LABEL_STYLE = """
    QLabel {
        font-family: 'Segoe UI', Arial;
        font-size: 13px;
        color: #444444;
    }
"""

FORM_INPUT_STYLE = """
    QLineEdit, QComboBox, QTextEdit, QSpinBox {
        font-family: 'Segoe UI', Arial;
        font-size: 13px;
        padding: 5px;
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        background-color: #FFFFFF;
    }
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QSpinBox:focus {
        border: 1px solid #2196F3;
    }
"""

# Dashboard styles
DASHBOARD_TITLE_STYLE = """
    QLabel {
        font-family: 'Segoe UI', Arial;
        font-size: 20px;
        font-weight: bold;
        color: #333333;
    }
"""

DASHBOARD_SUBTITLE_STYLE = """
    QLabel {
        font-family: 'Segoe UI', Arial;
        font-size: 16px;
        color: #555555;
    }
"""

# Modal dialog styles
DIALOG_TITLE_STYLE = """
    QLabel {
        font-family: 'Segoe UI', Arial;
        font-size: 18px;
        font-weight: bold;
        color: #333333;
    }
"""

# Tab styles
TAB_STYLE = """
    QTabWidget::pane { 
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        background-color: white;
        top: -1px; 
    }
    QTabBar::tab {
        font-family: 'Segoe UI', Arial;
        font-size: 13px;
        background-color: #F5F5F5;
        border: 1px solid #E0E0E0;
        border-bottom-color: #E0E0E0;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        min-width: 100px;
        padding: 8px;
    }
    QTabBar::tab:selected {
        background-color: white;
        border-bottom-color: white;
    }
    QTabBar::tab:hover:!selected {
        background-color: #EEEEEE;
    }
""" 