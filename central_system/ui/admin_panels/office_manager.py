#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Office Manager Panel

This module provides a panel for managing office information in the admin interface.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QLineEdit, QComboBox, 
                            QFormLayout, QTableWidget, QTableWidgetItem,
                            QHeaderView, QDialog, QMessageBox, QSpacerItem,
                            QSizePolicy, QCheckBox, QGroupBox, QDialogButtonBox,
                            QSpinBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from utils.logger import get_logger
from utils.error_handler import show_error_dialog, show_warning_dialog, show_confirmation_dialog

class OfficeDialog(QDialog):
    """
    Dialog for adding or editing office information.
    """
    
    def __init__(self, office=None, parent=None):
        """
        Initialize the office dialog.
        
        Args:
            office (dict, optional): Office data for editing, None for adding
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.office = office
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle("Office Information")
        self.setMinimumWidth(400)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        
        # Office ID
        self.id_input = QLineEdit()
        self.id_input.setObjectName("admin-input")
        form_layout.addRow("Office ID:", self.id_input)
        
        # Name/Description
        self.name_input = QLineEdit()
        self.name_input.setObjectName("admin-input")
        form_layout.addRow("Name/Description:", self.name_input)
        
        # Building
        self.building_input = QLineEdit()
        self.building_input.setObjectName("admin-input")
        form_layout.addRow("Building:", self.building_input)
        
        # Floor
        self.floor_spin = QSpinBox()
        self.floor_spin.setObjectName("admin-input")
        self.floor_spin.setMinimum(1)
        self.floor_spin.setMaximum(99)
        form_layout.addRow("Floor:", self.floor_spin)
        
        # Room
        self.room_input = QLineEdit()
        self.room_input.setObjectName("admin-input")
        form_layout.addRow("Room:", self.room_input)
        
        # BLE Beacon ID
        self.beacon_input = QLineEdit()
        self.beacon_input.setObjectName("admin-input")
        self.beacon_input.setPlaceholderText("Optional")
        form_layout.addRow("BLE Beacon ID:", self.beacon_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.setObjectName("admin-combo")
        self.status_combo.addItems(["Active", "Inactive", "Maintenance"])
        form_layout.addRow("Status:", self.status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Fill form if editing
        if self.office:
            self.id_input.setText(self.office.get('office_id', ''))
            self.name_input.setText(self.office.get('name', ''))
            self.building_input.setText(self.office.get('building', ''))
            self.room_input.setText(self.office.get('room', ''))
            self.beacon_input.setText(self.office.get('ble_beacon_id', ''))
            
            # Set floor
            floor = self.office.get('floor', 1)
            try:
                floor = int(floor)
                if 1 <= floor <= 99:
                    self.floor_spin.setValue(floor)
            except (ValueError, TypeError):
                self.floor_spin.setValue(1)
                
            # Set status
            status = self.office.get('status', 'Active')
            index = self.status_combo.findText(status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
            
    def get_office_data(self):
        """
        Get office data from the form.
        
        Returns:
            dict: Office data
        """
        office_data = {
            'office_id': self.id_input.text().strip(),
            'name': self.name_input.text().strip(),
            'building': self.building_input.text().strip(),
            'floor': self.floor_spin.value(),
            'room': self.room_input.text().strip(),
            'ble_beacon_id': self.beacon_input.text().strip(),
            'status': self.status_combo.currentText(),
            'last_updated': datetime.now().isoformat()
        }
        
        return office_data
        
    def validate(self):
        """
        Validate the form.
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Office ID is required
        if not self.id_input.text().strip():
            show_warning_dialog(
                title="Validation Error", 
                message="Office ID is required.",
                details="Please enter an office ID."
            )
            return False
            
        # Building is required
        if not self.building_input.text().strip():
            show_warning_dialog(
                title="Validation Error", 
                message="Building is required.",
                details="Please enter a building name."
            )
            return False
            
        # Room is required
        if not self.room_input.text().strip():
            show_warning_dialog(
                title="Validation Error", 
                message="Room is required.",
                details="Please enter a room number or identifier."
            )
            return False
            
        return True
        
    def accept(self):
        """Handle dialog acceptance."""
        if self.validate():
            super().accept()

class OfficeManagerPanel(QWidget):
    """
    Office manager panel for the admin interface.
    Allows administrators to add, edit, and delete office information.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the office manager panel.
        
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
        header = QLabel("Office Management")
        header.setObjectName("section-header")
        header.setFont(QFont("Roboto", 18, QFont.Weight.Bold))
        main_layout.addWidget(header)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Add button
        add_button = QPushButton("Add Office")
        add_button.setObjectName("primary-button")
        add_button.clicked.connect(self.add_office)
        controls_layout.addWidget(add_button)
        
        # Edit button
        self.edit_button = QPushButton("Edit Office")
        self.edit_button.setObjectName("secondary-button")
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.edit_office)
        controls_layout.addWidget(self.edit_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete Office")
        self.delete_button.setObjectName("secondary-button")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_office)
        controls_layout.addWidget(self.delete_button)
        
        # Spacer
        controls_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Filter
        filter_label = QLabel("Filter:")
        controls_layout.addWidget(filter_label)
        
        # Building filter
        self.building_filter = QComboBox()
        self.building_filter.setObjectName("admin-combo")
        self.building_filter.addItem("All Buildings")
        self.building_filter.currentTextChanged.connect(self.apply_filters)
        controls_layout.addWidget(self.building_filter)
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.setObjectName("admin-combo")
        self.status_filter.addItem("All Statuses")
        self.status_filter.addItems(["Active", "Inactive", "Maintenance"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        controls_layout.addWidget(self.status_filter)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search-input")
        self.search_input.setPlaceholderText("Search offices...")
        self.search_input.textChanged.connect(self.apply_filters)
        controls_layout.addWidget(self.search_input)
        
        main_layout.addLayout(controls_layout)
        
        # Office table
        self.office_table = QTableWidget()
        self.office_table.setObjectName("admin-table")
        self.office_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.office_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.office_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.office_table.setAlternatingRowColors(True)
        self.office_table.setColumnCount(7)
        self.office_table.setHorizontalHeaderLabels([
            "Office ID", "Name", "Building", "Floor", "Room", "Beacon ID", "Status"
        ])
        self.office_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.office_table.verticalHeader().setVisible(False)
        self.office_table.itemSelectionChanged.connect(self.handle_office_selection)
        main_layout.addWidget(self.office_table)
        
    def refresh_data(self):
        """Refresh office data from the database."""
        self.logger.info("Refreshing office data")
        
        # Clear table
        self.office_table.setRowCount(0)
        
        # Get all offices
        try:
            office_list = self.db_manager.get_all_offices()
            
            if not office_list:
                self.logger.warning("No offices found")
                return
                
            self.logger.info(f"Loaded {len(office_list)} offices")
            
            # Get unique buildings for filter
            buildings = set()
            for office in office_list:
                if 'building' in office and office['building']:
                    buildings.add(office['building'])
            
            # Update building filter
            current_building = self.building_filter.currentText()
            self.building_filter.clear()
            self.building_filter.addItem("All Buildings")
            for building in sorted(buildings):
                self.building_filter.addItem(building)
            
            # Restore selection if possible
            index = self.building_filter.findText(current_building)
            if index >= 0:
                self.building_filter.setCurrentIndex(index)
            
            # Populate table
            self.office_table.setRowCount(len(office_list))
            for row, office in enumerate(office_list):
                # Office ID
                id_item = QTableWidgetItem(office.get('office_id', ''))
                id_item.setData(Qt.ItemDataRole.UserRole, office)  # Store office data
                self.office_table.setItem(row, 0, id_item)
                
                # Name
                name_item = QTableWidgetItem(office.get('name', ''))
                self.office_table.setItem(row, 1, name_item)
                
                # Building
                building_item = QTableWidgetItem(office.get('building', ''))
                self.office_table.setItem(row, 2, building_item)
                
                # Floor
                floor_item = QTableWidgetItem(str(office.get('floor', '')))
                self.office_table.setItem(row, 3, floor_item)
                
                # Room
                room_item = QTableWidgetItem(office.get('room', ''))
                self.office_table.setItem(row, 4, room_item)
                
                # Beacon ID
                beacon_item = QTableWidgetItem(office.get('ble_beacon_id', ''))
                self.office_table.setItem(row, 5, beacon_item)
                
                # Status
                status_item = QTableWidgetItem(office.get('status', 'Active'))
                self.office_table.setItem(row, 6, status_item)
                
                # Set status color
                status = office.get('status', 'Active')
                if status == 'Active':
                    status_item.setForeground(QColor("#28a745"))
                elif status == 'Maintenance':
                    status_item.setForeground(QColor("#ffc107"))
                else:
                    status_item.setForeground(QColor("#dc3545"))
            
            # Apply filters
            self.apply_filters()
            
        except Exception as e:
            self.logger.error(f"Error refreshing office data: {e}")
            show_error_dialog(
                title="Data Error",
                message="Failed to load office data",
                details=str(e)
            )
            
    def apply_filters(self):
        """Apply filters to the office table."""
        search_text = self.search_input.text().lower()
        building = self.building_filter.currentText()
        status = self.status_filter.currentText()
        
        for row in range(self.office_table.rowCount()):
            # Get office data
            office_item = self.office_table.item(row, 0)
            if not office_item:
                continue
                
            show_row = True
            
            # Building filter
            if building != "All Buildings":
                building_item = self.office_table.item(row, 2)
                if not building_item or building_item.text() != building:
                    show_row = False
            
            # Status filter
            if status != "All Statuses" and show_row:
                status_item = self.office_table.item(row, 6)
                if not status_item or status_item.text() != status:
                    show_row = False
                    
            # Search text
            if search_text and show_row:
                text_match = False
                for col in range(7):
                    item = self.office_table.item(row, col)
                    if item and search_text in item.text().lower():
                        text_match = True
                        break
                
                show_row = text_match
                
            # Show/hide row
            self.office_table.setRowHidden(row, not show_row)
            
    def handle_office_selection(self):
        """Handle office selection in the table."""
        selected_items = self.office_table.selectedItems()
        
        # Enable/disable buttons
        has_selection = len(selected_items) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
    def add_office(self):
        """Add a new office."""
        self.logger.info("Adding new office")
        
        # Show dialog
        dialog = OfficeDialog(parent=self)
        if dialog.exec():
            # Get office data
            office_data = dialog.get_office_data()
            
            try:
                # Add to database
                success = self.db_manager.add_office(office_data)
                
                if not success:
                    show_error_dialog(
                        title="Add Office", 
                        message="Failed to add office",
                        details="The operation was unsuccessful. Please try again."
                    )
                    return
                    
                self.logger.info(f"Office added: {office_data.get('office_id')}")
                
                # Add audit log
                self.db_manager.add_audit_log({
                    'action': 'add_office',
                    'user_id': 'admin',  # Should be replaced with actual admin ID
                    'details': f"Added office: {office_data.get('name')} ({office_data.get('office_id')})"
                })
                
                # Refresh office data
                self.refresh_data()
                
                # Show success message
                QMessageBox.information(self, "Add Office", "Office added successfully.")
                
            except Exception as e:
                self.logger.error(f"Error adding office: {e}")
                show_error_dialog(
                    title="Add Office", 
                    message="Error adding office",
                    details=str(e)
                )
                
    def edit_office(self):
        """Edit selected office."""
        selected_items = self.office_table.selectedItems()
        if not selected_items:
            return
            
        # Get office data
        row = selected_items[0].row()
        office = self.office_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        self.logger.info(f"Editing office: {office.get('office_id')}")
        
        # Show dialog
        dialog = OfficeDialog(office, parent=self)
        if dialog.exec():
            # Get updated office data
            office_data = dialog.get_office_data()
            
            try:
                # Update in database
                success = self.db_manager.update_office(office.get('office_id'), office_data)
                
                if not success:
                    show_error_dialog(
                        title="Edit Office", 
                        message="Failed to update office",
                        details="The operation was unsuccessful. Please try again."
                    )
                    return
                    
                self.logger.info(f"Office updated: {office.get('office_id')}")
                
                # Add audit log
                self.db_manager.add_audit_log({
                    'action': 'edit_office',
                    'user_id': 'admin',  # Should be replaced with actual admin ID
                    'details': f"Updated office: {office_data.get('name')} ({office.get('office_id')})"
                })
                
                # Refresh office data
                self.refresh_data()
                
                # Show success message
                QMessageBox.information(self, "Edit Office", "Office updated successfully.")
                
            except Exception as e:
                self.logger.error(f"Error updating office: {e}")
                show_error_dialog(
                    title="Edit Office", 
                    message="Error updating office",
                    details=str(e)
                )
                
    def delete_office(self):
        """Delete selected office."""
        selected_items = self.office_table.selectedItems()
        if not selected_items:
            return
            
        # Get office data
        row = selected_items[0].row()
        office = self.office_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        self.logger.info(f"Deleting office: {office.get('office_id')}")
        
        # Confirm deletion
        if show_confirmation_dialog(
            title="Delete Office",
            message=f"Are you sure you want to delete office {office.get('name')}?",
            details="This action cannot be undone."
        ):
            try:
                # Delete from database
                success = self.db_manager.delete_office(office.get('office_id'))
                
                if not success:
                    show_error_dialog(
                        title="Delete Office", 
                        message="Failed to delete office",
                        details="The operation was unsuccessful. Please try again."
                    )
                    return
                    
                self.logger.info(f"Office deleted: {office.get('office_id')}")
                
                # Add audit log
                self.db_manager.add_audit_log({
                    'action': 'delete_office',
                    'user_id': 'admin',  # Should be replaced with actual admin ID
                    'details': f"Deleted office: {office.get('name')} ({office.get('office_id')})"
                })
                
                # Refresh office data
                self.refresh_data()
                
                # Show success message
                QMessageBox.information(self, "Delete Office", "Office deleted successfully.")
                
            except Exception as e:
                self.logger.error(f"Error deleting office: {e}")
                show_error_dialog(
                    title="Delete Office", 
                    message="Error deleting office",
                    details=str(e)
                ) 