#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Faculty History Viewer

This module provides a dialog for viewing faculty status history.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QComboBox, QDateEdit, QDialogButtonBox,
                            QFormLayout, QFrame)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QColor
from utils.logger import get_logger

class FacultyHistoryViewer(QDialog):
    """Dialog for viewing faculty status history."""
    
    def __init__(self, faculty, parent=None):
        """
        Initialize the faculty history viewer.
        
        Args:
            faculty (dict): Faculty data including status history
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.faculty = faculty
        self.history = faculty.get('status_history', [])
        
        self.setWindowTitle(f"Status History - {faculty.get('name', '')}")
        self.setMinimumSize(600, 400)
        
        self.init_ui()
        self.populate_history()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Header with faculty info
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_frame.setFrameShadow(QFrame.Shadow.Raised)
        info_layout = QFormLayout(info_frame)
        
        name_label = QLabel(f"<b>{self.faculty.get('name', 'Unknown')}</b>")
        info_layout.addRow("Name:", name_label)
        
        department_label = QLabel(self.faculty.get('department', 'Unknown'))
        info_layout.addRow("Department:", department_label)
        
        office_label = QLabel(self.faculty.get('office', 'Unknown'))
        info_layout.addRow("Office:", office_label)
        
        current_status = self.faculty.get('status', 'unavailable')
        status_label = QLabel(current_status.capitalize())
        
        # Set color based on status
        if current_status == 'available':
            status_label.setStyleSheet("color: #4ECDC4;")  # Green
        elif current_status == 'busy':
            status_label.setStyleSheet("color: #FFD166;")  # Amber
        else:
            status_label.setStyleSheet("color: #FF6B6B;")  # Red
            
        info_layout.addRow("Current Status:", status_label)
        
        main_layout.addWidget(info_frame)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Date range filter
        self.start_date = QDateEdit()
        self.start_date.setDateTime(QDateTime.currentDateTime().addDays(-7))
        self.start_date.setCalendarPopup(True)
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setDateTime(QDateTime.currentDateTime())
        self.end_date.setCalendarPopup(True)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_date)
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses")
        self.status_filter.addItem("Available")
        self.status_filter.addItem("Busy")
        self.status_filter.addItem("Unavailable")
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        
        # Apply filter button
        filter_button = QPushButton("Apply Filter")
        filter_button.clicked.connect(self.apply_filter)
        filter_layout.addWidget(filter_button)
        
        main_layout.addLayout(filter_layout)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Status", "Reason"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.history_table)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
    def populate_history(self):
        """Populate the history table with faculty status history."""
        # Clear table
        self.history_table.setRowCount(0)
        
        # Get filtered history
        filtered_history = self.get_filtered_history()
        
        if not filtered_history:
            self.logger.warning("No status history available")
            return
            
        # Sort by timestamp (newest first)
        filtered_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
        # Add history entries to table
        self.history_table.setRowCount(len(filtered_history))
        for row, entry in enumerate(filtered_history):
            # Timestamp
            timestamp = entry.get('timestamp', '')
            try:
                # Format timestamp for display
                dt = datetime.fromisoformat(timestamp)
                timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp_str = timestamp
                
            timestamp_item = QTableWidgetItem(timestamp_str)
            self.history_table.setItem(row, 0, timestamp_item)
            
            # Status
            status = entry.get('status', 'unknown')
            status_item = QTableWidgetItem(status.capitalize())
            
            # Set color based on status
            if status == 'available':
                status_item.setForeground(QColor('#4ECDC4'))  # Green
            elif status == 'busy':
                status_item.setForeground(QColor('#FFD166'))  # Amber
            else:
                status_item.setForeground(QColor('#FF6B6B'))  # Red
                
            self.history_table.setItem(row, 1, status_item)
            
            # Reason
            reason = entry.get('reason', '')
            reason_item = QTableWidgetItem(reason)
            self.history_table.setItem(row, 2, reason_item)
            
    def get_filtered_history(self):
        """
        Get filtered status history based on current filter settings.
        
        Returns:
            list: Filtered status history
        """
        # Start with all history
        filtered = self.history[:]
        
        # Apply date filter
        start_date = self.start_date.dateTime().toPython()
        end_date = self.end_date.dateTime().toPython()
        
        filtered = [
            entry for entry in filtered 
            if self.entry_in_date_range(entry, start_date, end_date)
        ]
        
        # Apply status filter
        status_filter = self.status_filter.currentText().lower()
        if status_filter != "all statuses":
            filtered = [
                entry for entry in filtered 
                if entry.get('status', '') == status_filter
            ]
            
        return filtered
        
    def entry_in_date_range(self, entry, start_date, end_date):
        """
        Check if an entry's timestamp is within the specified date range.
        
        Args:
            entry (dict): History entry
            start_date (datetime): Start date
            end_date (datetime): End date
            
        Returns:
            bool: True if entry is within range, False otherwise
        """
        try:
            timestamp = entry.get('timestamp', '')
            entry_date = datetime.fromisoformat(timestamp)
            return start_date <= entry_date <= end_date
        except:
            return False
            
    def apply_filter(self):
        """Apply current filter settings and update the display."""
        self.populate_history() 