#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Manual Login Dialog

This module provides a dialog for manual student login.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QFormLayout, QDialogButtonBox,
                            QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from utils.logger import get_logger
from utils.error_handler import show_error_dialog
from data.models import Student

class ManualLoginDialog(QDialog):
    """Dialog for manual student login."""
    
    def __init__(self, db_manager, parent=None):
        """
        Initialize the manual login dialog.
        
        Args:
            db_manager: Database manager instance
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.student = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Manual Login")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Student Login")
        title.setFont(QFont("Roboto", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Form layout
        form = QFormLayout()
        form.setSpacing(10)
        
        # ID input
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter your student ID")
        form.addRow("Student ID:", self.id_input)
        
        # Email input (alternative login method)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Or enter your email address")
        form.addRow("Email:", self.email_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.verify_login)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Set focus to ID input
        self.id_input.setFocus()
        
    def verify_login(self):
        """Verify login credentials and accept dialog if valid."""
        student_id = self.id_input.text().strip()
        email = self.email_input.text().strip()
        
        if not student_id and not email:
            QMessageBox.warning(self, "Missing Information", 
                              "Please enter either a student ID or email address.")
            return
            
        try:
            # Try to find student by ID
            if student_id:
                student_data = self.db_manager.get_student_by_id(student_id)
                if student_data:
                    self.student = Student.from_dict(student_data)
                    self.student.record_login()
                    self.db_manager.update_student(self.student.student_id, self.student.to_dict())
                    self.accept()
                    return
                    
            # If not found by ID, try email
            if email:
                student_data = self.db_manager.get_student_by_email(email)
                if student_data:
                    self.student = Student.from_dict(student_data)
                    self.student.record_login()
                    self.db_manager.update_student(self.student.student_id, self.student.to_dict())
                    self.accept()
                    return
                    
            # If we get here, no student was found
            QMessageBox.warning(self, "Login Failed", 
                              "No student found with the provided credentials.")
                              
        except Exception as e:
            self.logger.error(f"Error during manual login: {e}")
            show_error_dialog(
                title="Login Error",
                message="An error occurred during login",
                details=str(e)
            )
            
    def get_student(self):
        """
        Get the authenticated student.
        
        Returns:
            Student: Student instance if login successful, None otherwise
        """
        return self.student 