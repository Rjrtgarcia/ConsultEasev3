#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Admin Login Dialog

This module provides a dialog for admin user login.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QFormLayout, QDialogButtonBox,
                            QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap

from utils.logger import get_logger
from utils.error_handler import show_error_dialog

class AdminLoginDialog(QDialog):
    """Dialog for admin user login."""
    
    def __init__(self, db_manager, parent=None):
        """
        Initialize the admin login dialog.
        
        Args:
            db_manager: Database manager instance
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.admin_user = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Admin Login")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Administrator Login")
        title.setFont(QFont("Roboto", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Admin icon
        icon_path = "ui/assets/admin_icon.png"
        try:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                icon_label = QLabel()
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
                layout.addWidget(icon_label)
        except Exception as e:
            self.logger.warning(f"Could not load admin icon: {e}")
        
        # Form layout
        form = QFormLayout()
        form.setSpacing(10)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter admin username")
        form.addRow("Username:", self.username_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Password:", self.password_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.verify_login)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Set focus to username input
        self.username_input.setFocus()
        
    def verify_login(self):
        """Verify admin login credentials and accept dialog if valid."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Missing Information", 
                              "Please enter both username and password.")
            return
            
        try:
            # Verify admin credentials
            admin_user = self.db_manager.verify_admin_login(username, password)
            
            if admin_user:
                self.admin_user = admin_user
                
                # Log the admin login
                self.db_manager.add_audit_log({
                    'action': 'admin_login',
                    'user_id': admin_user.get('id'),
                    'username': username,
                    'details': f"Admin login"
                })
                
                self.accept()
            else:
                QMessageBox.warning(self, "Login Failed", 
                                  "Invalid username or password.")
                                  
        except Exception as e:
            self.logger.error(f"Error during admin login: {e}")
            show_error_dialog(
                title="Login Error",
                message="An error occurred during login",
                details=str(e)
            )
            
    def get_admin_user(self):
        """
        Get the authenticated admin user.
        
        Returns:
            dict: Admin user data if login successful, None otherwise
        """
        return self.admin_user 