#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Student Manager Panel

This module provides a panel for managing student information in the admin interface.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QLineEdit, QComboBox, 
                            QFormLayout, QTableWidget, QTableWidgetItem,
                            QHeaderView, QDialog, QMessageBox, QSpacerItem,
                            QSizePolicy, QCheckBox, QGroupBox, QDialogButtonBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from utils.logger import get_logger
from utils.error_handler import show_error_dialog, show_warning_dialog, show_confirmation_dialog

class StudentDialog(QDialog):
    """
    Dialog for adding or editing student information.
    """
    
    def __init__(self, student=None, parent=None):
        """
        Initialize the student dialog.
        
        Args:
            student (dict, optional): Student data for editing, None for adding
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.student = student
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle("Student Information")
        self.setMinimumWidth(400)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        
        # Student ID
        self.id_input = QLineEdit()
        self.id_input.setObjectName("admin-input")
        form_layout.addRow("Student ID:", self.id_input)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setObjectName("admin-input")
        form_layout.addRow("Name:", self.name_input)
        
        # Program
        self.program_input = QLineEdit()
        self.program_input.setObjectName("admin-input")
        form_layout.addRow("Program:", self.program_input)
        
        # Year Level
        self.year_combo = QComboBox()
        self.year_combo.setObjectName("admin-combo")
        for i in range(1, 6):  # 1-5 years
            self.year_combo.addItem(f"Year {i}")
        form_layout.addRow("Year Level:", self.year_combo)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setObjectName("admin-input")
        form_layout.addRow("Email:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setObjectName("admin-input")
        form_layout.addRow("Phone:", self.phone_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Fill form if editing
        if self.student:
            self.id_input.setText(self.student.get('student_id', ''))
            self.name_input.setText(self.student.get('name', ''))
            self.program_input.setText(self.student.get('program', ''))
            self.email_input.setText(self.student.get('email', ''))
            self.phone_input.setText(self.student.get('phone', ''))
            
            # Set year level
            year = self.student.get('year_level', 1)
            try:
                year = int(year)
                if 1 <= year <= 5:
                    self.year_combo.setCurrentIndex(year - 1)
            except (ValueError, TypeError):
                self.year_combo.setCurrentIndex(0)  # Default to Year 1
            
    def get_student_data(self):
        """
        Get student data from the form.
        
        Returns:
            dict: Student data
        """
        year_level = int(self.year_combo.currentText().split()[1])
        
        student_data = {
            'student_id': self.id_input.text().strip(),
            'name': self.name_input.text().strip(),
            'program': self.program_input.text().strip(),
            'year_level': year_level,
            'email': self.email_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'last_updated': datetime.now().isoformat()
        }
        
        return student_data
        
    def validate(self):
        """
        Validate the form.
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Student ID is required
        if not self.id_input.text().strip():
            show_warning_dialog(
                title="Validation Error", 
                message="Student ID is required.",
                details="Please enter a student ID."
            )
            return False
            
        # Name is required
        if not self.name_input.text().strip():
            show_warning_dialog(
                title="Validation Error", 
                message="Name is required.",
                details="Please enter a name for the student."
            )
            return False
            
        # Program is required
        if not self.program_input.text().strip():
            show_warning_dialog(
                title="Validation Error", 
                message="Program is required.",
                details="Please enter a program for the student."
            )
            return False
            
        return True
        
    def accept(self):
        """Handle dialog acceptance."""
        if self.validate():
            super().accept()

class StudentManagerPanel(QWidget):
    """
    Student manager panel for the admin interface.
    Allows administrators to add, edit, and delete student information.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the student manager panel.
        
        Args:
            db_manager: Database manager instance
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        
        # Header
        header = QLabel("Student Management")
        header.setObjectName("section-header")
        header.setFont(QFont("Roboto", 18, QFont.Weight.Bold))
        main_layout.addWidget(header)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Add button
        add_button = QPushButton("Add Student")
        add_button.setObjectName("primary-button")
        add_button.clicked.connect(self.add_student)
        controls_layout.addWidget(add_button)
        
        # Edit button
        self.edit_button = QPushButton("Edit Student")
        self.edit_button.setObjectName("secondary-button")
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.edit_student)
        controls_layout.addWidget(self.edit_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete Student")
        self.delete_button.setObjectName("secondary-button")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_student)
        controls_layout.addWidget(self.delete_button)
        
        # Spacer
        controls_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Filter
        filter_label = QLabel("Filter:")
        controls_layout.addWidget(filter_label)
        
        # Program filter
        self.program_filter = QComboBox()
        self.program_filter.setObjectName("admin-combo")
        self.program_filter.addItem("All Programs")
        self.program_filter.currentTextChanged.connect(self.apply_filters)
        controls_layout.addWidget(self.program_filter)
        
        # Year level filter
        self.year_filter = QComboBox()
        self.year_filter.setObjectName("admin-combo")
        self.year_filter.addItem("All Years")
        for i in range(1, 6):
            self.year_filter.addItem(f"Year {i}")
        self.year_filter.currentTextChanged.connect(self.apply_filters)
        controls_layout.addWidget(self.year_filter)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search-input")
        self.search_input.setPlaceholderText("Search students...")
        self.search_input.textChanged.connect(self.apply_filters)
        controls_layout.addWidget(self.search_input)
        
        main_layout.addLayout(controls_layout)
        
        # Student table
        self.student_table = QTableWidget()
        self.student_table.setObjectName("admin-table")
        self.student_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.student_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.student_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.student_table.setAlternatingRowColors(True)
        self.student_table.setColumnCount(6)
        self.student_table.setHorizontalHeaderLabels([
            "Student ID", "Name", "Program", "Year", "Email", "Phone"
        ])
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.student_table.verticalHeader().setVisible(False)
        self.student_table.itemSelectionChanged.connect(self.handle_student_selection)
        main_layout.addWidget(self.student_table)
        
    def refresh_data(self):
        """Refresh student data from the database."""
        self.logger.info("Refreshing student data")
        
        # Clear table
        self.student_table.setRowCount(0)
        
        # Get all students
        try:
            student_list = self.db_manager.get_all_students()
            
            if not student_list:
                self.logger.warning("No students found")
                return
                
            self.logger.info(f"Loaded {len(student_list)} students")
            
            # Get unique programs for filter
            programs = set()
            for student in student_list:
                if 'program' in student and student['program']:
                    programs.add(student['program'])
            
            # Update program filter
            current_program = self.program_filter.currentText()
            self.program_filter.clear()
            self.program_filter.addItem("All Programs")
            for program in sorted(programs):
                self.program_filter.addItem(program)
            
            # Restore selection if possible
            index = self.program_filter.findText(current_program)
            if index >= 0:
                self.program_filter.setCurrentIndex(index)
            
            # Populate table
            self.student_table.setRowCount(len(student_list))
            for row, student in enumerate(student_list):
                # Student ID
                id_item = QTableWidgetItem(student.get('student_id', ''))
                id_item.setData(Qt.ItemDataRole.UserRole, student)  # Store student data
                self.student_table.setItem(row, 0, id_item)
                
                # Name
                name_item = QTableWidgetItem(student.get('name', ''))
                self.student_table.setItem(row, 1, name_item)
                
                # Program
                program_item = QTableWidgetItem(student.get('program', ''))
                self.student_table.setItem(row, 2, program_item)
                
                # Year
                year_item = QTableWidgetItem(f"Year {student.get('year_level', 1)}")
                self.student_table.setItem(row, 3, year_item)
                
                # Email
                email_item = QTableWidgetItem(student.get('email', ''))
                self.student_table.setItem(row, 4, email_item)
                
                # Phone
                phone_item = QTableWidgetItem(student.get('phone', ''))
                self.student_table.setItem(row, 5, phone_item)
            
            # Apply filters
            self.apply_filters()
            
        except Exception as e:
            self.logger.error(f"Error refreshing student data: {e}")
            show_error_dialog(
                title="Data Error",
                message="Failed to load student data",
                details=str(e)
            )
            
    def apply_filters(self):
        """Apply filters to the student table."""
        search_text = self.search_input.text().lower()
        program = self.program_filter.currentText()
        year = self.year_filter.currentText()
        
        for row in range(self.student_table.rowCount()):
            # Get student data
            student_item = self.student_table.item(row, 0)
            if not student_item:
                continue
                
            show_row = True
            
            # Program filter
            if program != "All Programs":
                program_item = self.student_table.item(row, 2)
                if not program_item or program_item.text() != program:
                    show_row = False
            
            # Year filter
            if year != "All Years" and show_row:
                year_item = self.student_table.item(row, 3)
                if not year_item or year_item.text() != year:
                    show_row = False
                    
            # Search text
            if search_text and show_row:
                text_match = False
                for col in range(6):
                    item = self.student_table.item(row, col)
                    if item and search_text in item.text().lower():
                        text_match = True
                        break
                
                show_row = text_match
                
            # Show/hide row
            self.student_table.setRowHidden(row, not show_row)
            
    def handle_student_selection(self):
        """Handle student selection in the table."""
        selected_items = self.student_table.selectedItems()
        
        # Enable/disable buttons
        has_selection = len(selected_items) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
    def add_student(self):
        """Add a new student."""
        self.logger.info("Adding new student")
        
        # Show dialog
        dialog = StudentDialog(parent=self)
        if dialog.exec():
            # Get student data
            student_data = dialog.get_student_data()
            
            try:
                # Add to database
                success = self.db_manager.add_student(student_data)
                
                if not success:
                    show_error_dialog(
                        title="Add Student", 
                        message="Failed to add student",
                        details="The operation was unsuccessful. Please try again."
                    )
                    return
                    
                self.logger.info(f"Student added: {student_data.get('student_id')}")
                
                # Add audit log
                self.db_manager.add_audit_log({
                    'action': 'add_student',
                    'user_id': 'admin',  # Should be replaced with actual admin ID
                    'details': f"Added student: {student_data.get('name')} ({student_data.get('student_id')})"
                })
                
                # Refresh student data
                self.refresh_data()
                
                # Show success message
                QMessageBox.information(self, "Add Student", "Student added successfully.")
                
            except Exception as e:
                self.logger.error(f"Error adding student: {e}")
                show_error_dialog(
                    title="Add Student", 
                    message="Error adding student",
                    details=str(e)
                )
                
    def edit_student(self):
        """Edit selected student."""
        selected_items = self.student_table.selectedItems()
        if not selected_items:
            return
            
        # Get student data
        row = selected_items[0].row()
        student = self.student_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        self.logger.info(f"Editing student: {student.get('student_id')}")
        
        # Show dialog
        dialog = StudentDialog(student, parent=self)
        if dialog.exec():
            # Get updated student data
            student_data = dialog.get_student_data()
            
            try:
                # Update in database
                success = self.db_manager.update_student(student.get('student_id'), student_data)
                
                if not success:
                    show_error_dialog(
                        title="Edit Student", 
                        message="Failed to update student",
                        details="The operation was unsuccessful. Please try again."
                    )
                    return
                    
                self.logger.info(f"Student updated: {student.get('student_id')}")
                
                # Add audit log
                self.db_manager.add_audit_log({
                    'action': 'edit_student',
                    'user_id': 'admin',  # Should be replaced with actual admin ID
                    'details': f"Updated student: {student_data.get('name')} ({student.get('student_id')})"
                })
                
                # Refresh student data
                self.refresh_data()
                
                # Show success message
                QMessageBox.information(self, "Edit Student", "Student updated successfully.")
                
            except Exception as e:
                self.logger.error(f"Error updating student: {e}")
                show_error_dialog(
                    title="Edit Student", 
                    message="Error updating student",
                    details=str(e)
                )
                
    def delete_student(self):
        """Delete selected student."""
        selected_items = self.student_table.selectedItems()
        if not selected_items:
            return
            
        # Get student data
        row = selected_items[0].row()
        student = self.student_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        self.logger.info(f"Deleting student: {student.get('student_id')}")
        
        # Confirm deletion
        if show_confirmation_dialog(
            title="Delete Student",
            message=f"Are you sure you want to delete {student.get('name')}?",
            details="This action cannot be undone."
        ):
            try:
                # Delete from database
                success = self.db_manager.delete_student(student.get('student_id'))
                
                if not success:
                    show_error_dialog(
                        title="Delete Student", 
                        message="Failed to delete student",
                        details="The operation was unsuccessful. Please try again."
                    )
                    return
                    
                self.logger.info(f"Student deleted: {student.get('student_id')}")
                
                # Add audit log
                self.db_manager.add_audit_log({
                    'action': 'delete_student',
                    'user_id': 'admin',  # Should be replaced with actual admin ID
                    'details': f"Deleted student: {student.get('name')} ({student.get('student_id')})"
                })
                
                # Refresh student data
                self.refresh_data()
                
                # Show success message
                QMessageBox.information(self, "Delete Student", "Student deleted successfully.")
                
            except Exception as e:
                self.logger.error(f"Error deleting student: {e}")
                show_error_dialog(
                    title="Delete Student", 
                    message="Error deleting student",
                    details=str(e)
                ) 