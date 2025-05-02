#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Request Manager Admin Panel

This module provides the request manager admin panel for the ConsultEase application.
It allows administrators to view and manage consultation requests.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                            QMessageBox, QComboBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QFont, QIcon

from utils.logger import get_logger
from utils.error_handler import show_error_dialog, show_warning_dialog, show_confirmation_dialog

class RequestManagerPanel(QWidget):
    """
    Request manager admin panel for managing consultation requests.
    
    Signals:
        status_message (str): Emitted when a status message should be displayed
    """
    status_message = pyqtSignal(str)
    
    def __init__(self, db_manager, mqtt_client, parent=None):
        """
        Initialize the request manager panel.
        
        Args:
            db_manager: Database manager instance
            mqtt_client: MQTT client instance
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.mqtt_client = mqtt_client
        
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
        header_label = QLabel("Consultation Requests")
        header_label.setObjectName("panel-header")
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(header_label)
        
        # Add spacer to push buttons to the right
        header_layout.addStretch()
        
        # Add refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName("action-button")
        refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_button)
        
        # Add header to main layout
        main_layout.addLayout(header_layout)
        
        # Create table for consultation requests
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(6)
        self.requests_table.setHorizontalHeaderLabels([
            "ID", "Student", "Course", "Faculty", "Status", "Date"
        ])
        
        # Set column properties
        header = self.requests_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.requests_table.setAlternatingRowColors(True)
        self.requests_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.requests_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        main_layout.addWidget(self.requests_table)
        
        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
    def refresh_data(self):
        """Refresh data from the database."""
        self.logger.info("Refreshing request data")
        self.status_label.setText("Loading consultation requests...")
        
        # Clear table
        self.requests_table.setRowCount(0)
        
        # In a real implementation, you would load data here
        # For now, just update the status
        self.status_label.setText("Ready - Request Manager functionality will be implemented here")
        
    @pyqtSlot()
    def handle_request_selection(self):
        """Handle selection of a request in the table."""
        selected_rows = self.requests_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        # In a real implementation, you would handle the selection here
        
    def clear_table(self):
        """Clear the request table."""
        self.requests_table.setRowCount(0) 