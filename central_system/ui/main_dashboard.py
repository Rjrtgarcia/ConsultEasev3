#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Main Dashboard

This module provides the main dashboard for the ConsultEase application.
It displays faculty availability and allows students to submit consultation requests.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QLineEdit, QTextEdit, QComboBox,
                            QScrollArea, QGridLayout, QSplitter, QGroupBox, 
                            QFormLayout, QMessageBox, QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon, QColor

from data.models import Faculty, Student, ConsultationRequest
from utils.logger import get_logger
from utils.error_handler import show_error_dialog, show_warning_dialog

class FacultyCard(QFrame):
    """
    Widget to display faculty information in a card format.
    """
    
    def __init__(self, faculty, parent=None):
        """
        Initialize the faculty card.
        
        Args:
            faculty (dict): Faculty data
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.faculty = faculty
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setObjectName("faculty-card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Faculty name
        name_label = QLabel(self.faculty.get('name', 'Unknown'))
        name_label.setObjectName("faculty-name")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(name_label)
        
        # Department
        dept_label = QLabel(self.faculty.get('department', 'Unknown Department'))
        dept_label.setObjectName("faculty-department")
        layout.addWidget(dept_label)
        
        # Office
        office_label = QLabel(f"Office: {self.faculty.get('office', 'Unknown')}")
        office_label.setObjectName("faculty-office")
        layout.addWidget(office_label)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 5, 0, 0)
        
        status_label = QLabel("Status:")
        status_layout.addWidget(status_label)
        
        self.status_indicator = QLabel(self.faculty.get('status', 'unavailable').capitalize())
        self.status_indicator.setObjectName(f"status-{self.faculty.get('status', 'unavailable')}")
        
        # Set color based on status
        if self.faculty.get('status') == 'available':
            self.status_indicator.setStyleSheet("color: #2ecc71; font-weight: bold;")  # Green
        else:
            self.status_indicator.setStyleSheet("color: #e74c3c; font-weight: bold;")  # Red
            
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
        
        # Set color based on status
        if status == 'available':
            self.status_indicator.setStyleSheet("color: #2ecc71; font-weight: bold;")  # Green
        else:
            self.status_indicator.setStyleSheet("color: #e74c3c; font-weight: bold;")  # Red

class NotificationItem(QFrame):
    """
    Widget to display a notification item.
    """
    
    def __init__(self, message, timestamp=None, parent=None):
        """
        Initialize the notification item.
        
        Args:
            message (str): Notification message
            timestamp (datetime, optional): Notification timestamp
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.message = message
        self.timestamp = timestamp or datetime.now()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setObjectName("notification-item")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(50)
        self.setMaximumHeight(80)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)
        
        # Timestamp
        time_str = self.timestamp.strftime("%H:%M")
        time_label = QLabel(time_str)
        time_label.setObjectName("notification-time")
        time_label.setFont(QFont("Arial", 8))
        layout.addWidget(time_label)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setObjectName("notification-message")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

class MainDashboard(QMainWindow):
    """
    Main dashboard for the ConsultEase application.
    Displays faculty availability and allows students to submit consultation requests.
    """
    
    def __init__(self, db_manager, mqtt_client, student):
        """
        Initialize the main dashboard.
        
        Args:
            db_manager: Database manager instance
            mqtt_client: MQTT client instance
            student (dict): Student data
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.mqtt_client = mqtt_client
        self.student = student
        
        # Connect MQTT signals
        self.mqtt_client.faculty_status_changed.connect(self.handle_faculty_status_change)
        self.mqtt_client.message_received.connect(self.handle_mqtt_message)
        
        # Initialize UI
        self.init_ui()
        
        # Load faculty data
        self.load_faculty_data()
        
        # Start auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("ConsultEase - Dashboard")
        self.setMinimumSize(1024, 768)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Logo (placeholder)
        logo_label = QLabel("ConsultEase")
        logo_label.setObjectName("logo-label")
        logo_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(logo_label)
        
        # Spacer
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Student info
        student_info = QLabel(f"Welcome, {self.student.get('name', 'Student')}")
        student_info.setObjectName("student-info")
        header_layout.addWidget(student_info)
        
        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.setObjectName("text-button")
        logout_button.clicked.connect(self.logout)
        header_layout.addWidget(logout_button)
        
        main_layout.addLayout(header_layout)
        
        # Content area
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setHandleWidth(1)
        content_splitter.setChildrenCollapsible(False)
        
        # Left panel - Faculty availability
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # Faculty panel header
        faculty_header = QLabel("Faculty Availability")
        faculty_header.setObjectName("panel-header")
        faculty_header.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(faculty_header)
        
        # Faculty filter controls
        filter_layout = QHBoxLayout()
        
        # Department filter
        dept_label = QLabel("Department:")
        filter_layout.addWidget(dept_label)
        
        self.dept_combo = QComboBox()
        self.dept_combo.setObjectName("filter-combo")
        self.dept_combo.addItem("All Departments")
        self.dept_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.dept_combo)
        
        # Status filter
        status_label = QLabel("Status:")
        filter_layout.addWidget(status_label)
        
        self.status_combo = QComboBox()
        self.status_combo.setObjectName("filter-combo")
        self.status_combo.addItem("All")
        self.status_combo.addItem("Available")
        self.status_combo.addItem("Unavailable")
        self.status_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.status_combo)
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName("text-button")
        refresh_button.clicked.connect(self.refresh_data)
        filter_layout.addWidget(refresh_button)
        
        left_layout.addLayout(filter_layout)
        
        # Faculty list scroll area
        faculty_scroll = QScrollArea()
        faculty_scroll.setWidgetResizable(True)
        faculty_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        faculty_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.faculty_container = QWidget()
        self.faculty_layout = QVBoxLayout(self.faculty_container)
        self.faculty_layout.setContentsMargins(0, 0, 0, 0)
        self.faculty_layout.setSpacing(10)
        self.faculty_layout.addStretch()
        
        faculty_scroll.setWidget(self.faculty_container)
        left_layout.addWidget(faculty_scroll)
        
        # Right panel - Consultation request and notifications
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(20)
        
        # Consultation request section
        request_group = QGroupBox("Consultation Request")
        request_group.setObjectName("request-group")
        request_layout = QVBoxLayout(request_group)
        
        # Faculty selection
        faculty_form = QFormLayout()
        
        self.faculty_combo = QComboBox()
        self.faculty_combo.setObjectName("request-combo")
        faculty_form.addRow("Faculty:", self.faculty_combo)
        
        # Course code
        self.course_input = QLineEdit()
        self.course_input.setObjectName("request-input")
        self.course_input.setPlaceholderText("e.g., CS101")
        faculty_form.addRow("Course Code:", self.course_input)
        
        request_layout.addLayout(faculty_form)
        
        # Request text
        request_layout.addWidget(QLabel("Request Details:"))
        
        self.request_text = QTextEdit()
        self.request_text.setObjectName("request-text")
        self.request_text.setPlaceholderText("Enter your consultation request details here...")
        self.request_text.setMinimumHeight(100)
        request_layout.addWidget(self.request_text)
        
        # Submit button
        submit_button = QPushButton("Submit Request")
        submit_button.setObjectName("primary-button")
        submit_button.clicked.connect(self.submit_request)
        request_layout.addWidget(submit_button)
        
        right_layout.addWidget(request_group)
        
        # Notifications section
        notif_group = QGroupBox("Notifications")
        notif_group.setObjectName("notif-group")
        notif_layout = QVBoxLayout(notif_group)
        
        # Notifications scroll area
        notif_scroll = QScrollArea()
        notif_scroll.setWidgetResizable(True)
        notif_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        notif_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.notif_container = QWidget()
        self.notif_layout = QVBoxLayout(self.notif_container)
        self.notif_layout.setContentsMargins(0, 0, 0, 0)
        self.notif_layout.setSpacing(5)
        self.notif_layout.addStretch()
        
        notif_scroll.setWidget(self.notif_container)
        notif_layout.addWidget(notif_scroll)
        
        right_layout.addWidget(notif_group)
        
        # Add panels to splitter
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([500, 500])  # Initial sizes
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def load_faculty_data(self):
        """Load faculty data from the database."""
        self.logger.info("Loading faculty data")
        self.statusBar().showMessage("Loading faculty data...")
        
        # Clear existing faculty cards
        self.clear_faculty_layout()
        
        # Get all faculty
        faculty_list = self.db_manager.get_all_faculty()
        
        if not faculty_list:
            self.logger.warning("No faculty found")
            self.statusBar().showMessage("No faculty found")
            return
            
        self.logger.info(f"Loaded {len(faculty_list)} faculty members")
        
        # Collect departments for filter
        departments = set()
        
        # Create faculty cards
        self.faculty_cards = {}
        for faculty in faculty_list:
            # Add to faculty combo box
            self.faculty_combo.addItem(faculty.get('name', 'Unknown'), faculty.get('id'))
            
            # Create faculty card
            card = FacultyCard(faculty)
            self.faculty_cards[faculty.get('id')] = card
            self.faculty_layout.insertWidget(self.faculty_layout.count() - 1, card)
            
            # Add department to set
            if faculty.get('department'):
                departments.add(faculty.get('department'))
                
        # Update department filter
        self.dept_combo.clear()
        self.dept_combo.addItem("All Departments")
        for dept in sorted(departments):
            self.dept_combo.addItem(dept)
            
        # Add initial notification
        self.add_notification("Welcome to ConsultEase!")
        self.add_notification("Faculty availability is updated in real-time.")
        
        self.statusBar().showMessage("Faculty data loaded")
        
    def clear_faculty_layout(self):
        """Clear the faculty layout."""
        # Remove all faculty cards
        while self.faculty_layout.count() > 1:
            item = self.faculty_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Clear faculty combo box
        self.faculty_combo.clear()
        
    def apply_filters(self):
        """Apply filters to faculty list."""
        dept_filter = self.dept_combo.currentText()
        status_filter = self.status_combo.currentText().lower()
        
        # Show/hide faculty cards based on filters
        for faculty_id, card in self.faculty_cards.items():
            faculty = card.faculty
            
            # Department filter
            dept_match = (dept_filter == "All Departments" or 
                         faculty.get('department') == dept_filter)
            
            # Status filter
            status_match = (status_filter == "all" or 
                           faculty.get('status') == status_filter)
            
            # Show/hide card
            card.setVisible(dept_match and status_match)
            
    def refresh_data(self):
        """Refresh faculty data."""
        self.logger.info("Refreshing faculty data")
        self.statusBar().showMessage("Refreshing faculty data...")
        
        # Get all faculty
        faculty_list = self.db_manager.get_all_faculty()
        
        if not faculty_list:
            self.logger.warning("No faculty found")
            self.statusBar().showMessage("No faculty found")
            return
            
        # Update faculty cards
        for faculty in faculty_list:
            faculty_id = faculty.get('id')
            if faculty_id in self.faculty_cards:
                # Update existing card
                self.faculty_cards[faculty_id].faculty = faculty
                self.faculty_cards[faculty_id].update_status(faculty.get('status', 'unavailable'))
                
        # Apply filters
        self.apply_filters()
        
        self.statusBar().showMessage("Faculty data refreshed")
        self.add_notification("Faculty data refreshed")
        
    def handle_faculty_status_change(self, faculty_id, status):
        """
        Handle faculty status change from MQTT.
        
        Args:
            faculty_id (str): Faculty ID
            status (str): New status
        """
        self.logger.info(f"Faculty status change: {faculty_id} -> {status}")
        
        if faculty_id in self.faculty_cards:
            # Update faculty card
            self.faculty_cards[faculty_id].update_status(status)
            
            # Add notification
            faculty_name = self.faculty_cards[faculty_id].faculty.get('name', 'Unknown')
            self.add_notification(f"Faculty {faculty_name} is now {status}")
            
            # Apply filters
            self.apply_filters()
            
    def handle_mqtt_message(self, topic, payload):
        """
        Handle MQTT message.
        
        Args:
            topic (str): Message topic
            payload (str): Message payload
        """
        self.logger.debug(f"MQTT message: {topic} - {payload}")
        
        # Handle specific topics if needed
        if topic == "consultease/notifications":
            try:
                import json
                data = json.loads(payload)
                message = data.get('message', 'System notification')
                self.add_notification(message)
            except Exception as e:
                self.logger.error(f"Error processing notification: {e}")
                
    def add_notification(self, message):
        """
        Add a notification to the notifications panel.
        
        Args:
            message (str): Notification message
        """
        # Create notification item
        notif = NotificationItem(message)
        
        # Add to layout (at the top)
        self.notif_layout.insertWidget(0, notif)
        
        # Limit to 10 notifications
        if self.notif_layout.count() > 11:  # 10 notifications + stretch
            item = self.notif_layout.takeAt(self.notif_layout.count() - 2)
            if item.widget():
                item.widget().deleteLater()
                
    def submit_request(self):
        """Submit a consultation request."""
        # Get selected faculty
        faculty_index = self.faculty_combo.currentIndex()
        if faculty_index < 0:
            show_warning_dialog(self, "Consultation Request", 
                               "Please select a faculty member.")
            return
            
        faculty_id = self.faculty_combo.itemData(faculty_index)
        faculty_name = self.faculty_combo.itemText(faculty_index)
        
        # Get course code
        course_code = self.course_input.text().strip()
        
        # Get request text
        request_text = self.request_text.toPlainText().strip()
        if not request_text:
            show_warning_dialog(self, "Consultation Request", 
                               "Please enter request details.")
            return
            
        # Create request data
        request_data = {
            'student_id': self.student.get('id'),
            'faculty_id': faculty_id,
            'request_text': request_text,
            'course_code': course_code,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"Submitting consultation request: {request_data}")
        
        try:
            # Add to database
            request_id = self.db_manager.add_consultation_request(request_data)
            
            if not request_id:
                show_error_dialog(self, "Consultation Request", 
                                 "Failed to submit request. Please try again.")
                return
                
            # Publish to MQTT
            self.mqtt_client.publish_consultation_request(request_data)
            
            # Show success message
            QMessageBox.information(self, "Consultation Request", 
                                   f"Request submitted successfully to {faculty_name}.")
            
            # Clear form
            self.course_input.clear()
            self.request_text.clear()
            
            # Add notification
            self.add_notification(f"Consultation request submitted to {faculty_name}")
            
        except Exception as e:
            self.logger.error(f"Error submitting request: {e}")
            show_error_dialog(self, "Consultation Request", 
                             f"Error submitting request: {str(e)}")
            
    def logout(self):
        """Log out and return to login screen."""
        self.logger.info("Logging out")
        
        # Confirm logout
        reply = QMessageBox.question(self, "Logout", 
                                    "Are you sure you want to log out?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Stop refresh timer
            self.refresh_timer.stop()
            
            # Close dashboard
            self.close()
            
            # Show login screen
            from ui.login_screen import LoginScreen
            self.login_screen = LoginScreen(self.db_manager, self.mqtt_client)
            self.login_screen.show()
            
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        self.logger.info("Closing dashboard")
        
        # Stop refresh timer
        self.refresh_timer.stop()
        
        # Accept the event
        event.accept()
