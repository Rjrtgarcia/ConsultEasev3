#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Faculty Manager Panel

This module provides a panel for managing faculty information in the admin interface.
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
from data.models import Faculty

# List of common academic departments
COMMON_DEPARTMENTS = [
    "Computer Science",
    "Information Technology",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Business Administration",
    "Economics",
    "Psychology",
    "Sociology",
    "Political Science",
    "History",
    "English",
    "Communication",
    "Fine Arts",
    "Music",
    "Education",
    "Nursing",
    "Medicine",
    "Pharmacy",
    "Law",
    "Architecture",
    "Other"
]

class FacultyDialog(QDialog):
    """
    Dialog for adding or editing faculty information.
    """
    
    def __init__(self, faculty=None, parent=None):
        """
        Initialize the faculty dialog.
        
        Args:
            faculty (dict, optional): Faculty data for editing, None for adding
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.faculty = faculty
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle("Faculty Information")
        self.setMinimumWidth(400)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setObjectName("admin-input")
        form_layout.addRow("Name:", self.name_input)
        
        # Department - Changed from LineEdit to ComboBox with common departments
        self.dept_combo = QComboBox()
        self.dept_combo.setObjectName("admin-combo")
        self.dept_combo.setEditable(True)  # Allow custom departments
        self.dept_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Don't add new items to list
        
        # Add common departments
        for dept in COMMON_DEPARTMENTS:
            self.dept_combo.addItem(dept)
            
        # Add custom department option
        self.dept_combo.addItem("Custom...")
        self.dept_combo.currentTextChanged.connect(self._handle_department_selection)
        
        # Custom department input (initially hidden)
        self.custom_dept_input = QLineEdit()
        self.custom_dept_input.setObjectName("admin-input")
        self.custom_dept_input.setPlaceholderText("Enter custom department name")
        self.custom_dept_input.setVisible(False)
        
        # Department layout
        dept_layout = QVBoxLayout()
        dept_layout.setSpacing(5)
        dept_layout.addWidget(self.dept_combo)
        dept_layout.addWidget(self.custom_dept_input)
        
        form_layout.addRow("Department:", dept_layout)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setObjectName("admin-input")
        form_layout.addRow("Email:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setObjectName("admin-input")
        form_layout.addRow("Phone:", self.phone_input)
        
        # Office
        self.office_input = QLineEdit()
        self.office_input.setObjectName("admin-input")
        form_layout.addRow("Office:", self.office_input)
        
        # BLE Beacon ID
        self.ble_input = QLineEdit()
        self.ble_input.setObjectName("admin-input")
        self.ble_input.setPlaceholderText("e.g., AA:BB:CC:DD:EE:FF")
        form_layout.addRow("BLE Beacon ID:", self.ble_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.setObjectName("admin-combo")
        self.status_combo.addItem("Available")
        self.status_combo.addItem("Unavailable")
        form_layout.addRow("Status:", self.status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Fill form if editing
        if self.faculty:
            self.name_input.setText(self.faculty.get('name', ''))
            
            # Find the department in the list or set custom
            department = self.faculty.get('department', '')
            index = self.dept_combo.findText(department)
            if index >= 0:
                self.dept_combo.setCurrentIndex(index)
            else:
                # Set to custom and fill in the custom field
                custom_index = self.dept_combo.findText("Custom...")
                if custom_index >= 0:
                    self.dept_combo.setCurrentIndex(custom_index)
                    self.custom_dept_input.setText(department)
                    self.custom_dept_input.setVisible(True)
            
            self.email_input.setText(self.faculty.get('email', ''))
            self.phone_input.setText(self.faculty.get('phone', ''))
            self.office_input.setText(self.faculty.get('office', ''))
            self.ble_input.setText(self.faculty.get('ble_beacon_id', ''))
            
            status_index = 0 if self.faculty.get('status') == 'available' else 1
            self.status_combo.setCurrentIndex(status_index)
    
    def _handle_department_selection(self, text):
        """Handle department selection change."""
        if text == "Custom...":
            self.custom_dept_input.setVisible(True)
        else:
            self.custom_dept_input.setVisible(False)
            
    def get_faculty_data(self):
        """
        Get faculty data from the form.
        
        Returns:
            dict: Faculty data
        """
        # Get department (from combo or custom input)
        if self.dept_combo.currentText() == "Custom...":
            department = self.custom_dept_input.text().strip()
        else:
            department = self.dept_combo.currentText().strip()
            
        faculty_data = {
            'name': self.name_input.text().strip(),
            'department': department,
            'email': self.email_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'office': self.office_input.text().strip(),
            'ble_beacon_id': self.ble_input.text().strip(),
            'status': 'available' if self.status_combo.currentText() == 'Available' else 'unavailable',
            'last_updated': datetime.now().isoformat()
        }
        
        # Add ID if editing
        if self.faculty and 'id' in self.faculty:
            faculty_data['id'] = self.faculty['id']
            
        return faculty_data
        
    def validate(self):
        """
        Validate the form.
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Name is required
        if not self.name_input.text().strip():
            show_warning_dialog(
                title="Validation Error", 
                message="Name is required.",
                details="Please enter a name for the faculty member."
            )
            return False
            
        # Department is required
        department = ""
        if self.dept_combo.currentText() == "Custom...":
            department = self.custom_dept_input.text().strip()
        else:
            department = self.dept_combo.currentText().strip()
            
        if not department:
            show_warning_dialog(
                title="Validation Error", 
                message="Department is required.",
                details="Please select or enter a department for the faculty member."
            )
            return False
            
        # BLE Beacon ID format validation (simple check)
        ble_id = self.ble_input.text().strip()
        if ble_id and not self._validate_ble_id(ble_id):
            show_warning_dialog(
                title="Validation Error", 
                message="Invalid BLE Beacon ID format.",
                details="BLE Beacon ID should be in the format AA:BB:CC:DD:EE:FF."
            )
            return False
            
        return True
        
    def _validate_ble_id(self, ble_id):
        """
        Validate BLE Beacon ID format.
        
        Args:
            ble_id (str): BLE Beacon ID
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Simple format check (could be more sophisticated)
        parts = ble_id.split(':')
        if len(parts) != 6:
            return False
            
        for part in parts:
            if len(part) != 2 or not all(c in '0123456789ABCDEFabcdef' for c in part):
                return False
                
        return True
        
    def accept(self):
        """Handle dialog acceptance."""
        if self.validate():
            super().accept()

class FacultyManagerPanel(QWidget):
    """
    Faculty management panel for the admin interface.
    
    Provides functionality for managing faculty members (add, edit, delete).
    """
    
    def __init__(self, db_manager, mqtt_client, parent=None):
        """
        Initialize the faculty manager panel.
        
        Args:
            db_manager: Database manager instance
            mqtt_client: MQTT client instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.mqtt_client = mqtt_client
        
        # Initialize UI
        self.init_ui()
        
        # Load data
        self.refresh_data()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        label = QLabel("Faculty Management")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(label)
        header_layout.addStretch()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        self.dept_filter = QComboBox()
        self.dept_filter.addItem("All Departments")
        filter_layout.addWidget(QLabel("Department:"))
        filter_layout.addWidget(self.dept_filter)
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses")
        self.status_filter.addItem("Available")
        self.status_filter.addItem("Unavailable")
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search faculty...")
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_input)
        
        # Connect signals
        self.dept_filter.currentIndexChanged.connect(self.apply_filters)
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        self.search_input.textChanged.connect(self.apply_filters)
        
        # Add filter layout to header
        header_layout.addLayout(filter_layout)
        
        main_layout.addLayout(header_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Faculty")
        self.add_button.setObjectName("primary-button")
        self.add_button.clicked.connect(self.add_faculty)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.edit_faculty)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.setEnabled(False)
        self.delete_button.setObjectName("danger-button")
        self.delete_button.clicked.connect(self.delete_faculty)
        button_layout.addWidget(self.delete_button)
        
        self.view_history_button = QPushButton("View Status History")
        self.view_history_button.setEnabled(False)
        self.view_history_button.clicked.connect(self.view_faculty_history)
        button_layout.addWidget(self.view_history_button)
        
        button_layout.addStretch()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(button_layout)
        
        # Faculty table
        self.faculty_table = QTableWidget()
        self.faculty_table.setColumnCount(7)
        
        self.faculty_table.setHorizontalHeaderLabels([
            "ID", "Name", "Department", "Email", "Office", "BLE ID", "Status"
        ])
        self.faculty_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.faculty_table.verticalHeader().setVisible(False)
        self.faculty_table.itemSelectionChanged.connect(self.handle_faculty_selection)
        main_layout.addWidget(self.faculty_table)
        
    def refresh_data(self):
        """Refresh faculty data from the database."""
        self.logger.info("Refreshing faculty data")
        
        # Clear table
        self.faculty_table.setRowCount(0)
        
        # Get all faculty
        try:
            faculty_list = self.db_manager.get_all_faculty()
            
            if not faculty_list:
                self.logger.warning("No faculty found")
                return
                
            self.logger.info(f"Loaded {len(faculty_list)} faculty members")
            
            # Get unique departments for filter
            departments = set()
            for faculty in faculty_list:
                if 'department' in faculty and faculty['department']:
                    departments.add(faculty['department'])
            
            # Update department filter
            current_dept = self.dept_filter.currentText()
            self.dept_filter.clear()
            self.dept_filter.addItem("All Departments")
            for dept in sorted(departments):
                self.dept_filter.addItem(dept)
            
            # Restore selection if possible
            index = self.dept_filter.findText(current_dept)
            if index >= 0:
                self.dept_filter.setCurrentIndex(index)
            
            # Populate table
            self.faculty_table.setRowCount(len(faculty_list))
            for row, faculty in enumerate(faculty_list):
                # ID
                id_item = QTableWidgetItem(faculty.get('id', ''))
                id_item.setData(Qt.ItemDataRole.UserRole, faculty)  # Store faculty data
                self.faculty_table.setItem(row, 0, id_item)
                
                # Name
                name_item = QTableWidgetItem(faculty.get('name', ''))
                self.faculty_table.setItem(row, 1, name_item)
                
                # Department
                dept_item = QTableWidgetItem(faculty.get('department', ''))
                self.faculty_table.setItem(row, 2, dept_item)
                
                # Email
                email_item = QTableWidgetItem(faculty.get('email', ''))
                self.faculty_table.setItem(row, 3, email_item)
                
                # Office
                office_item = QTableWidgetItem(faculty.get('office', ''))
                self.faculty_table.setItem(row, 4, office_item)
                
                # BLE ID
                ble_item = QTableWidgetItem(faculty.get('ble_beacon_id', ''))
                self.faculty_table.setItem(row, 5, ble_item)
                
                # Status
                status_item = QTableWidgetItem(faculty.get('status', 'unavailable').capitalize())
                
                # Set color based on status
                if faculty.get('status') == 'available':
                    status_item.setForeground(QColor('#4ECDC4'))  # Green (from theme)
                else:
                    status_item.setForeground(QColor('#FF6B6B'))  # Red (from theme)
                    
                self.faculty_table.setItem(row, 6, status_item)
            
            # Apply filters
            self.apply_filters()
            
        except Exception as e:
            self.logger.error(f"Error refreshing faculty data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load faculty data: {e}")
            
    def apply_filters(self):
        """Apply filters to the faculty table."""
        self.logger.info("Applying faculty filters")
        
        # Get filter values
        department = self.dept_filter.currentText()
        status = self.status_filter.currentText().lower()
        search_text = self.search_input.text().lower()
        
        # Show all rows first
        for row in range(self.faculty_table.rowCount()):
            self.faculty_table.setRowHidden(row, False)
            
        # Apply filters
        for row in range(self.faculty_table.rowCount()):
            # Get row data
            dept_item = self.faculty_table.item(row, 2)
            status_item = self.faculty_table.item(row, 6)
            name_item = self.faculty_table.item(row, 1)
            email_item = self.faculty_table.item(row, 3)
            
            dept_text = dept_item.text() if dept_item else ""
            status_text = status_item.text().lower() if status_item else ""
            name_text = name_item.text().lower() if name_item else ""
            email_text = email_item.text().lower() if email_item else ""
            
            # Check if row matches all filters
            dept_match = department == "All Departments" or dept_text == department
            status_match = status == "all statuses" or status_text == status
            search_match = (
                not search_text or 
                search_text in name_text or 
                search_text in email_text
            )
            
            # Hide row if it doesn't match any filter
            if not (dept_match and status_match and search_match):
                self.faculty_table.setRowHidden(row, True)
                
    def handle_faculty_selection(self):
        """Handle faculty selection in the table."""
        # Enable/disable buttons based on selection
        has_selection = len(self.faculty_table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.view_history_button.setEnabled(has_selection)
        
    def get_selected_faculty(self):
        """
        Get the currently selected faculty member.
        
        Returns:
            dict: Faculty data, or None if no faculty is selected
        """
        selected_items = self.faculty_table.selectedItems()
        if not selected_items:
            return None
            
        # Get the row of the first selected item
        row = selected_items[0].row()
        
        # Get the faculty data stored in the ID item
        id_item = self.faculty_table.item(row, 0)
        if not id_item:
            return None
            
        return id_item.data(Qt.ItemDataRole.UserRole)
        
    def add_faculty(self):
        """Add a new faculty member."""
        self.logger.info("Adding new faculty member")
        
        dialog = FacultyDialog(self.db_manager, parent=self)
        
        if dialog.exec():
            # Get faculty data
            faculty_data = dialog.get_faculty_data()
            
            try:
                # Add to database
                faculty_id = self.db_manager.add_faculty(faculty_data)
                
                if not faculty_id:
                    show_error_dialog(
                        title="Add Faculty", 
                        message="Failed to add faculty",
                        details="The operation was unsuccessful. Please try again."
                    )
                    return
                    
                self.logger.info(f"Faculty added: {faculty_id}")
                
                # Add audit log
                self.db_manager.add_audit_log({
                    'action': 'add_faculty',
                    'user_id': 'admin',  # Should be replaced with actual admin ID
                    'details': f"Added new faculty member: {faculty_data.get('name')}"
                })
                
                # Refresh faculty data
                self.refresh_data()
                
                # Show success message
                QMessageBox.information(self, "Add Faculty", "Faculty added successfully.")
                
            except Exception as e:
                self.logger.error(f"Error adding faculty: {e}")
                show_error_dialog(
                    title="Add Faculty", 
                    message="Error adding faculty",
                    details=str(e)
                )
                
    def edit_faculty(self):
        """Edit the selected faculty member."""
        self.logger.info("Editing faculty member")
        
        faculty = self.get_selected_faculty()
        if not faculty:
            self.logger.warning("No faculty selected for editing")
            return
            
        dialog = FacultyDialog(self.db_manager, faculty=faculty, parent=self)
        
        if dialog.exec():
            # Get updated faculty data
            faculty_data = dialog.get_faculty_data()
            
            try:
                # Update in database
                success = self.db_manager.update_faculty(faculty.get('id'), faculty_data)
                
                if not success:
                    show_error_dialog(
                        title="Edit Faculty", 
                        message="Failed to update faculty",
                        details="The operation was unsuccessful. Please try again."
                    )
                    return
                    
                self.logger.info(f"Faculty updated: {faculty.get('id')}")
                
                # Add audit log
                self.db_manager.add_audit_log({
                    'action': 'edit_faculty',
                    'user_id': 'admin',  # Should be replaced with actual admin ID
                    'details': f"Updated faculty member: {faculty_data.get('name')} ({faculty.get('id')})"
                })
                
                # Refresh faculty data
                self.refresh_data()
                
                # Show success message
                QMessageBox.information(self, "Edit Faculty", "Faculty updated successfully.")
                
                # Publish status update if changed
                if faculty.get('status') != faculty_data.get('status'):
                    self.mqtt_client.publish_faculty_status(
                        faculty.get('id'), faculty_data.get('status')
                    )
                
            except Exception as e:
                self.logger.error(f"Error updating faculty: {e}")
                show_error_dialog(
                    title="Edit Faculty", 
                    message="Error updating faculty",
                    details=str(e)
                )
                
    def delete_faculty(self):
        """Delete the selected faculty member."""
        self.logger.info("Deleting faculty member")
        
        faculty = self.get_selected_faculty()
        if not faculty:
            self.logger.warning("No faculty selected for deletion")
            return
            
        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {faculty.get('name')}?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result != QMessageBox.StandardButton.Yes:
            return
            
        try:
            # Delete from database
            success = self.db_manager.delete_faculty(faculty.get('id'))
            
            if not success:
                show_error_dialog(
                    title="Delete Faculty", 
                    message="Failed to delete faculty",
                    details="The operation was unsuccessful. Please try again."
                )
                return
                
            self.logger.info(f"Faculty deleted: {faculty.get('id')}")
            
            # Add audit log
            self.db_manager.add_audit_log({
                'action': 'delete_faculty',
                'user_id': 'admin',  # Should be replaced with actual admin ID
                'details': f"Deleted faculty member: {faculty.get('name')} ({faculty.get('id')})"
            })
            
            # Refresh faculty data
            self.refresh_data()
            
            # Show success message
            QMessageBox.information(self, "Delete Faculty", "Faculty deleted successfully.")
            
        except Exception as e:
            self.logger.error(f"Error deleting faculty: {e}")
            show_error_dialog(
                title="Delete Faculty", 
                message="Error deleting faculty",
                details=str(e)
            )
            
    def view_faculty_history(self):
        """View the selected faculty member's status history."""
        self.logger.info("Viewing faculty status history")
        
        faculty = self.get_selected_faculty()
        if not faculty:
            self.logger.warning("No faculty selected for viewing history")
            return
            
        # Import here to avoid circular imports
        from ui.admin_panels.faculty_history_viewer import FacultyHistoryViewer
        
        dialog = FacultyHistoryViewer(faculty, parent=self)
        dialog.exec() 