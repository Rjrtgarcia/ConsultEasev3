#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - System Settings Panel

This module provides a panel for managing system settings in the admin interface.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QLineEdit, QSpinBox, QCheckBox, QTabWidget,
                            QFormLayout, QGroupBox, QGridLayout, QComboBox,
                            QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QSettings, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QFont

from utils.logger import get_logger
from utils.error_handler import show_error_dialog, show_warning_dialog, show_confirmation_dialog

class SystemSettingsPanel(QWidget):
    """
    System settings panel for the admin interface.
    Allows administrators to configure system settings.
    
    Signals:
        settings_changed (dict): Emitted when settings are saved with the new settings
    """
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        Initialize the system settings panel.
        
        Args:
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        
        # Initialize settings
        self.settings = QSettings("ConsultEase", "ConsultEase")
        
        # Initialize UI
        self.init_ui()
        
        # Load settings
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("System Settings")
        title.setObjectName("panel-header")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Save button
        save_button = QPushButton("Save Settings")
        save_button.setObjectName("primary-button")
        save_button.clicked.connect(self.save_settings)
        header_layout.addWidget(save_button)
        
        # Reset button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.setObjectName("secondary-button")
        reset_button.clicked.connect(self.reset_to_defaults)
        header_layout.addWidget(reset_button)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget for settings categories
        self.tabs = QTabWidget()
        
        # General tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # System info group
        system_group = QGroupBox("System Information")
        system_form = QFormLayout(system_group)
        
        self.system_name_input = QLineEdit()
        self.system_name_input.setObjectName("settings-input")
        self.system_name_input.setPlaceholderText("Enter system name")
        system_form.addRow("System Name:", self.system_name_input)
        
        self.admin_email_input = QLineEdit()
        self.admin_email_input.setObjectName("settings-input")
        self.admin_email_input.setPlaceholderText("Enter admin email address")
        system_form.addRow("Admin Email:", self.admin_email_input)
        
        general_layout.addWidget(system_group)
        
        # Interface group
        interface_group = QGroupBox("User Interface")
        interface_form = QFormLayout(interface_group)
        
        self.touchscreen_check = QCheckBox("Enable Touchscreen Mode")
        self.touchscreen_check.setObjectName("settings-checkbox")
        self.touchscreen_check.setToolTip("Optimize UI for touch input")
        interface_form.addRow("", self.touchscreen_check)
        
        self.keyboard_check = QCheckBox("Enable On-Screen Keyboard")
        self.keyboard_check.setObjectName("settings-checkbox")
        self.keyboard_check.setToolTip("Show on-screen keyboard when text input is focused")
        interface_form.addRow("", self.keyboard_check)
        
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("settings-combo")
        self.theme_combo.addItems(["Light", "Dark", "High Contrast"])
        self.theme_combo.setToolTip("Set application theme")
        interface_form.addRow("Theme:", self.theme_combo)
        
        general_layout.addWidget(interface_group)
        
        # Add a status label
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status-label")
        general_layout.addWidget(self.status_label)
        
        # Add tabs
        self.tabs.addTab(general_tab, "General")
        self.tabs.addTab(QWidget(), "Network")
        self.tabs.addTab(QWidget(), "Hardware")
        self.tabs.addTab(QWidget(), "Security")
        self.tabs.addTab(QWidget(), "Backup")
        
        main_layout.addWidget(self.tabs)
        
    def load_settings(self):
        """Load settings from storage."""
        self.logger.info("Loading system settings")
        self.status_label.setText("Loading settings...")
        
        try:
            # Set default values if not already set
            if not self.settings.contains("system/name"):
                self.reset_to_defaults(silent=True)
                
            # Load values from settings
            self.system_name_input.setText(self.settings.value("system/name", "ConsultEase"))
            self.admin_email_input.setText(self.settings.value("system/admin_email", ""))
            self.touchscreen_check.setChecked(self.settings.value("interface/touchscreen", False, type=bool))
            self.keyboard_check.setChecked(self.settings.value("interface/keyboard", False, type=bool))
            
            # Theme
            theme_index = self.theme_combo.findText(self.settings.value("interface/theme", "Dark"))
            if theme_index >= 0:
                self.theme_combo.setCurrentIndex(theme_index)
                
            self.status_label.setText("Settings loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            show_error_dialog(
                title="Settings Error",
                message="Failed to load settings",
                details=str(e)
            )
            self.status_label.setText("Error loading settings")
        
    @pyqtSlot()
    def save_settings(self):
        """Save settings to storage."""
        self.logger.info("Saving system settings")
        self.status_label.setText("Saving settings...")
        
        try:
            # Validate settings before saving
            if not self._validate_settings():
                return
                
            # Collect current settings to emit in signal
            current_settings = {
                "system/name": self.system_name_input.text(),
                "system/admin_email": self.admin_email_input.text(),
                "interface/touchscreen": self.touchscreen_check.isChecked(),
                "interface/keyboard": self.keyboard_check.isChecked(),
                "interface/theme": self.theme_combo.currentText()
            }
            
            # Save values to settings
            for key, value in current_settings.items():
                self.settings.setValue(key, value)
            
            # Save and sync
            self.settings.sync()
            
            # Emit settings changed signal
            self.settings_changed.emit(current_settings)
            
            # Show confirmation
            self.status_label.setText("Settings saved successfully")
            QMessageBox.information(self, "Settings Saved", "System settings have been saved successfully.")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            show_error_dialog(
                title="Settings Error",
                message="Failed to save settings",
                details=str(e)
            )
            self.status_label.setText("Error saving settings")
        
    def reset_to_defaults(self, silent=False):
        """
        Reset settings to default values.
        
        Args:
            silent (bool): If True, don't show confirmation dialog
        """
        if silent or show_confirmation_dialog(
            title="Reset Settings",
            message="Are you sure you want to reset all settings to default values?",
            details="This cannot be undone."
        ):
            try:
                self.logger.info("Resetting system settings to defaults")
                self.status_label.setText("Resetting settings...")
                
                # Set default values
                self.system_name_input.setText("ConsultEase")
                self.admin_email_input.setText("")
                self.touchscreen_check.setChecked(False)
                self.keyboard_check.setChecked(False)
                self.theme_combo.setCurrentText("Dark")
                
                # Save defaults
                if not silent:
                    self.save_settings()
                    
                self.status_label.setText("Settings reset to defaults")
                
            except Exception as e:
                self.logger.error(f"Error resetting settings: {e}")
                if not silent:
                    show_error_dialog(
                        title="Settings Error",
                        message="Failed to reset settings",
                        details=str(e)
                    )
                self.status_label.setText("Error resetting settings")
                
    def _validate_settings(self):
        """
        Validate the settings before saving.
        
        Returns:
            bool: True if settings are valid, False otherwise
        """
        # Validate email if provided
        email = self.admin_email_input.text().strip()
        if email and "@" not in email:
            show_warning_dialog(
                title="Invalid Email",
                message="The admin email address is invalid.",
                details="Please enter a valid email address or leave it empty."
            )
            return False
            
        return True 