#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Faculty Card Component

This module defines a UI component that displays faculty information in a card format.
It is used to display faculty members in the dashboard and other parts of the application.
"""

from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from central_system.ui.utils.styles import (
    CARD_STYLE, 
    TITLE_LABEL_STYLE, 
    SUBTITLE_LABEL_STYLE, 
    INFO_LABEL_STYLE,
    STATUS_LABEL_STYLES
)

class FacultyCard(QFrame):
    """
    Widget to display faculty information in a card format.
    
    This component shows faculty details and status in a visually appealing card layout,
    allowing for quick scanning of faculty information and availability.
    
    Signals:
        clicked: Emitted when the card is clicked
    """
    
    # Signal emitted when the card is clicked
    clicked = pyqtSignal(dict)
    
    def __init__(self, faculty, parent=None):
        """
        Initialize the faculty card.
        
        Args:
            faculty (dict): Faculty data dictionary or Faculty model instance
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        
        # Convert Faculty model instance to dict if needed
        if not isinstance(faculty, dict):
            self.faculty = faculty.to_dict()
            if hasattr(faculty, 'faculty_id'):
                self.faculty['id'] = faculty.faculty_id
        else:
            self.faculty = faculty
            
        self.init_ui()
        self.setStyleSheet(CARD_STYLE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setObjectName("faculty-card")
        self.setMinimumHeight(140)  # Increased height to accommodate department
        self.setMaximumHeight(140)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Faculty name
        name_label = QLabel(self.faculty.get('name', 'Unknown'))
        name_label.setObjectName("faculty-name")
        name_label.setStyleSheet(TITLE_LABEL_STYLE)
        layout.addWidget(name_label)
        
        # Department - make it more prominent
        dept = self.faculty.get('department', 'Unknown Department')
        dept_label = QLabel(dept)
        dept_label.setObjectName("faculty-department")
        dept_label.setStyleSheet(SUBTITLE_LABEL_STYLE)
        dept_label.setFont(QFont("Roboto", 11, QFont.Weight.Bold))  # Make department stand out
        layout.addWidget(dept_label)
        
        # Office
        office_label = QLabel(f"Office: {self.faculty.get('office', 'Unknown')}")
        office_label.setObjectName("faculty-office")
        office_label.setStyleSheet(INFO_LABEL_STYLE)
        layout.addWidget(office_label)
        
        # Email (adding this for more comprehensive info)
        email = self.faculty.get('email', '')
        if email:
            email_label = QLabel(f"Email: {email}")
            email_label.setObjectName("faculty-email")
            email_label.setStyleSheet(INFO_LABEL_STYLE)
            layout.addWidget(email_label)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 5, 0, 0)
        
        status_label = QLabel("Status:")
        status_label.setStyleSheet(INFO_LABEL_STYLE)
        status_layout.addWidget(status_label)
        
        status = self.faculty.get('status', 'unavailable')
        self.status_indicator = QLabel(status.capitalize())
        self.status_indicator.setObjectName(f"status-{status}")
        
        # Set style based on status
        status_style = STATUS_LABEL_STYLES.get(status, STATUS_LABEL_STYLES['inactive'])
        self.status_indicator.setStyleSheet(status_style)
            
        status_layout.addWidget(self.status_indicator)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
    def update_status(self, status):
        """
        Update the faculty status.
        
        Args:
            status (str): New status
        """
        self.faculty['status'] = status
        self.status_indicator.setText(status.capitalize())
        self.status_indicator.setObjectName(f"status-{status}")
        
        # Set style based on status
        status_style = STATUS_LABEL_STYLES.get(status, STATUS_LABEL_STYLES['inactive'])
        self.status_indicator.setStyleSheet(status_style)
    
    def mousePressEvent(self, event):
        """Handle mouse press events to emit clicked signal."""
        self.clicked.emit(self.faculty)
        super().mousePressEvent(event) 