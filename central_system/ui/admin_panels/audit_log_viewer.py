#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Audit Log Viewer

This module provides a viewer for the audit log in the admin interface.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                            QSplitter, QComboBox, QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate, pyqtSlot
from PyQt6.QtGui import QFont, QColor

from utils.logger import get_logger
from utils.error_handler import show_error_dialog

class AuditLogViewerPanel(QWidget):
    """
    Audit log viewer panel for the admin interface.
    """
    
    def __init__(self, db_manager, parent=None):
        """
        Initialize the audit log viewer panel.
        
        Args:
            db_manager: Database manager instance
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        
        # Initialize UI
        self.init_ui()
        
        # Initial data load
        self.refresh_data()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Audit Log")
        title.setObjectName("panel-header")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # Spacer
        header_layout.addStretch()
        
        # Filter controls
        header_layout.addWidget(QLabel("Filter:"))
        
        self.action_filter = QComboBox()
        self.action_filter.addItem("All Actions")
        self.action_filter.addItem("Login")
        self.action_filter.addItem("Faculty Update")
        self.action_filter.addItem("Student Update")
        self.action_filter.addItem("System")
        self.action_filter.currentTextChanged.connect(self.apply_filters)
        header_layout.addWidget(self.action_filter)
        
        # Date filter
        header_layout.addWidget(QLabel("Date:"))
        
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.dateChanged.connect(self.apply_filters)
        header_layout.addWidget(self.date_filter)
        
        # Reset button
        self.reset_button = QPushButton("Reset Filters")
        self.reset_button.clicked.connect(self.reset_filters)
        header_layout.addWidget(self.reset_button)
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_button)
        
        main_layout.addLayout(header_layout)
        
        # Log table
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "Action", "User", "Details", "ID"])
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setSortingEnabled(True)
        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Set column widths
        header = self.log_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Details column stretches
        
        # Hide ID column - used for reference only
        self.log_table.setColumnHidden(4, True)
        
        main_layout.addWidget(self.log_table)
        
        # Status label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
    @pyqtSlot()
    def refresh_data(self):
        """Refresh audit log data from the database."""
        self.logger.info("Refreshing audit log data")
        self.status_label.setText("Loading audit log...")
        
        try:
            # Clear table
            self.log_table.setRowCount(0)
            
            # In a real implementation, you would load data from db_manager
            # For demonstration, show a placeholder message
            self.status_label.setText("Ready - Audit log functionality will be implemented here")
            
        except Exception as e:
            self.logger.error(f"Error refreshing audit log data: {e}")
            show_error_dialog(
                title="Refresh Error",
                message="Failed to refresh audit log data",
                details=str(e)
            )
            self.status_label.setText("Error loading audit log data")
        
    @pyqtSlot()
    def apply_filters(self):
        """Apply filters to the audit log data."""
        try:
            action_filter = self.action_filter.currentText()
            date_filter = self.date_filter.date().toString("yyyy-MM-dd")
            
            self.logger.info(f"Applying filters: Action={action_filter}, Date={date_filter}")
            self.status_label.setText(f"Filtering: {action_filter} on {date_filter}")
            
            # In a real implementation, you would apply filters to the data
            # For now, just acknowledge the filter change
            
        except Exception as e:
            self.logger.error(f"Error applying filters: {e}")
            self.status_label.setText("Error applying filters")
        
    @pyqtSlot()
    def reset_filters(self):
        """Reset filters to default values."""
        try:
            self.action_filter.setCurrentIndex(0)  # All Actions
            self.date_filter.setDate(QDate.currentDate())
            self.status_label.setText("Filters reset to defaults")
            self.refresh_data()
            
        except Exception as e:
            self.logger.error(f"Error resetting filters: {e}")
            self.status_label.setText("Error resetting filters") 