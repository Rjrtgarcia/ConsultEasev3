#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Office Card Component

This module defines the OfficeCard UI component which displays office information
in a card format for the ConsultEase application.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from central_system.ui.utils.styles import (
    CARD_STYLE, TITLE_LABEL_STYLE, SUBTITLE_LABEL_STYLE, 
    INFO_LABEL_STYLE, STATUS_LABEL_STYLES, ACTION_BUTTON_STYLE
)


class OfficeCard(QFrame):
    """
    A card component for displaying office information.
    
    This component displays office details including name, location, 
    status, and provides action buttons for viewing and editing the office.
    
    Signals:
        view_clicked (str): Signal emitted when the view button is clicked, 
                           with the office ID as parameter
        edit_clicked (str): Signal emitted when the edit button is clicked,
                           with the office ID as parameter
    """
    
    # Signals
    view_clicked = pyqtSignal(str)
    edit_clicked = pyqtSignal(str)
    
    def __init__(self, office, parent=None):
        """
        Initialize the office card.
        
        Args:
            office: Office model instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.office = office
        
        # Connect to data change signal
        self.office.data_changed.connect(self.update_ui)
        
        self.setup_ui()
        self.update_ui()
    
    def setup_ui(self):
        """Set up the UI components and layout."""
        # Apply card style
        self.setStyleSheet(CARD_STYLE)
        self.setMinimumWidth(300)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(8)
        
        # Office name label
        self.name_label = QLabel()
        self.name_label.setStyleSheet(TITLE_LABEL_STYLE)
        self.name_label.setWordWrap(True)
        
        # Location label
        self.location_label = QLabel()
        self.location_label.setStyleSheet(SUBTITLE_LABEL_STYLE)
        self.location_label.setWordWrap(True)
        
        # Status label
        self.status_container = QHBoxLayout()
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_container.addStretch()
        self.status_container.addWidget(self.status_label)
        self.status_container.addStretch()
        
        # BLE beacon ID label
        self.beacon_layout = QHBoxLayout()
        beacon_label = QLabel("Beacon ID:")
        beacon_label.setStyleSheet(INFO_LABEL_STYLE)
        self.beacon_value = QLabel()
        self.beacon_value.setStyleSheet(INFO_LABEL_STYLE)
        self.beacon_layout.addWidget(beacon_label)
        self.beacon_layout.addWidget(self.beacon_value)
        self.beacon_layout.addStretch()
        
        # Last updated label
        self.updated_layout = QHBoxLayout()
        updated_label = QLabel("Last updated:")
        updated_label.setStyleSheet(INFO_LABEL_STYLE)
        self.updated_value = QLabel()
        self.updated_value.setStyleSheet(INFO_LABEL_STYLE)
        self.updated_layout.addWidget(updated_label)
        self.updated_layout.addWidget(self.updated_value)
        self.updated_layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        # View button
        self.view_button = QPushButton("View")
        self.view_button.setStyleSheet(ACTION_BUTTON_STYLE)
        self.view_button.clicked.connect(self.on_view_clicked)
        
        # Edit button
        self.edit_button = QPushButton("Edit")
        self.edit_button.setStyleSheet(ACTION_BUTTON_STYLE)
        self.edit_button.clicked.connect(self.on_edit_clicked)
        
        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(self.view_button)
        button_layout.addWidget(self.edit_button)
        
        # Add all elements to main layout
        main_layout.addWidget(self.name_label)
        main_layout.addWidget(self.location_label)
        main_layout.addLayout(self.status_container)
        main_layout.addSpacerItem(QSpacerItem(20, 10))
        main_layout.addLayout(self.beacon_layout)
        main_layout.addLayout(self.updated_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 15))
        main_layout.addLayout(button_layout)
    
    def update_ui(self):
        """Update the UI based on the office data."""
        # Update office name
        if self.office.name:
            self.name_label.setText(self.office.name)
        else:
            self.name_label.setText("Unnamed Office")
        
        # Update location
        self.location_label.setText(self.office.get_location_string())
        
        # Update status label
        status = self.office.status
        self.status_label.setText(status.upper())
        
        # Apply appropriate status style
        if status.lower() == "active":
            self.status_label.setStyleSheet(STATUS_LABEL_STYLES.get("active"))
        elif status.lower() == "maintenance":
            self.status_label.setStyleSheet(STATUS_LABEL_STYLES.get("maintenance"))
        else:  # inactive or any other status
            self.status_label.setStyleSheet(STATUS_LABEL_STYLES.get("inactive"))
        
        # Update BLE beacon ID
        beacon_id = self.office.ble_beacon_id
        if beacon_id:
            self.beacon_value.setText(beacon_id)
        else:
            self.beacon_value.setText("Not assigned")
        
        # Update last updated timestamp
        last_updated = self.office.last_updated
        if last_updated:
            self.updated_value.setText(last_updated)
        else:
            self.updated_value.setText("Unknown")
    
    @pyqtSlot()
    def on_view_clicked(self):
        """Handle view button click event."""
        if self.office.office_id:
            self.view_clicked.emit(self.office.office_id)
    
    @pyqtSlot()
    def on_edit_clicked(self):
        """Handle edit button click event."""
        if self.office.office_id:
            self.edit_clicked.emit(self.office.office_id) 