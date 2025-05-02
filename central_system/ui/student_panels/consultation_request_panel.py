#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Consultation Request Panel

This module provides a panel for students to submit consultation requests to faculty members.
"""

import os
import uuid
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QTextEdit, QComboBox, QMessageBox, QFormLayout,
                            QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from data.models.consultation_request import ConsultationRequest
from utils.logger import get_logger
from utils.error_handler import show_error_dialog, show_info_dialog

class ConsultationRequestPanel(QWidget):
    """
    Panel for submitting consultation requests to faculty members.
    
    Signals:
        request_submitted (dict): Emitted when a request is submitted with the request details
    """
    request_submitted = pyqtSignal(dict)
    
    def __init__(self, db_manager, mqtt_client, student, parent=None):
        """
        Initialize the consultation request panel.
        
        Args:
            db_manager: Database manager instance
            mqtt_client: MQTT client instance
            student (dict): Student data
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.mqtt_client = mqtt_client
        self.student = student
        
        # Load faculty list
        self.faculty_list = []
        self.refresh_faculty_list()
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("Request Consultation")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Form frame
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        form_frame.setFrameShadow(QFrame.Shadow.Raised)
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setVerticalSpacing(10)
        
        # Faculty selection
        self.faculty_combo = QComboBox()
        self.faculty_combo.addItem("Select faculty member...")
        
        # Populate faculty combo
        for faculty in self.faculty_list:
            if faculty.get('status') == 'available':
                name = faculty.get('name', '')
                department = faculty.get('department', '')
                display_text = f"{name} ({department})"
                self.faculty_combo.addItem(display_text, userData=faculty)
                
        form_layout.addRow("Faculty:", self.faculty_combo)
        
        # Course code
        self.course_code_input = QLineEdit()
        self.course_code_input.setPlaceholderText("e.g., CS101, MATH202")
        form_layout.addRow("Course Code:", self.course_code_input)
        
        # Topic
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Brief topic of consultation")
        form_layout.addRow("Topic:", self.topic_input)
        
        # Request details
        self.details_input = QTextEdit()
        self.details_input.setPlaceholderText("Explain what you need help with...")
        self.details_input.setMinimumHeight(100)
        form_layout.addRow("Details:", self.details_input)
        
        # Preferred time (optional)
        self.time_combo = QComboBox()
        self.time_combo.addItem("As soon as possible")
        self.time_combo.addItem("Today")
        self.time_combo.addItem("Tomorrow")
        self.time_combo.addItem("This week")
        self.time_combo.addItem("Next week")
        form_layout.addRow("Preferred Time:", self.time_combo)
        
        # Add form to main layout
        main_layout.addWidget(form_frame)
        
        # Spacer
        main_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Reset button
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_form)
        button_layout.addWidget(reset_button)
        
        # Submit button
        submit_button = QPushButton("Submit Request")
        submit_button.setStyleSheet("background-color: #4ECDC4; color: white; font-weight: bold;")
        submit_button.clicked.connect(self.submit_request)
        button_layout.addWidget(submit_button)
        
        main_layout.addLayout(button_layout)
        
    def refresh_faculty_list(self):
        """Refresh the faculty list from the database."""
        try:
            # Get available faculty members
            self.faculty_list = self.db_manager.get_all_faculty()
            self.logger.info(f"Loaded {len(self.faculty_list)} faculty members")
            
        except Exception as e:
            self.logger.error(f"Error loading faculty list: {e}")
            self.faculty_list = []
            
    def reset_form(self):
        """Reset the form to its initial state."""
        self.faculty_combo.setCurrentIndex(0)
        self.course_code_input.clear()
        self.topic_input.clear()
        self.details_input.clear()
        self.time_combo.setCurrentIndex(0)
        
    def validate_form(self):
        """
        Validate the form inputs.
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Check faculty selection
        if self.faculty_combo.currentIndex() == 0:
            show_error_dialog(
                title="Validation Error",
                message="Please select a faculty member",
                details="You must select a faculty member to request a consultation."
            )
            return False
            
        # Check topic
        if not self.topic_input.text().strip():
            show_error_dialog(
                title="Validation Error",
                message="Please enter a topic",
                details="You must provide a topic for the consultation."
            )
            return False
            
        # Check request details
        if not self.details_input.toPlainText().strip():
            show_error_dialog(
                title="Validation Error",
                message="Please enter request details",
                details="You must provide details about what you need help with."
            )
            return False
            
        return True
        
    def submit_request(self):
        """Submit the consultation request."""
        # Validate form
        if not self.validate_form():
            return
            
        try:
            # Get form data
            faculty = self.faculty_combo.currentData()
            if not faculty:
                self.logger.error("No faculty data found in combo box")
                return
                
            # Create request data
            request_data = {
                'request_id': str(uuid.uuid4()),
                'student_id': self.student.get('id'),
                'student_name': self.student.get('name'),
                'faculty_id': faculty.get('id'),
                'faculty_name': faculty.get('name'),
                'course_code': self.course_code_input.text().strip(),
                'topic': self.topic_input.text().strip(),
                'details': self.details_input.toPlainText().strip(),
                'preferred_time': self.time_combo.currentText(),
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Log request details
            self.logger.info(f"Submitting consultation request: {request_data['topic']}")
            
            # Add to database
            request_id = self.db_manager.add_consultation_request(request_data)
            
            if not request_id:
                show_error_dialog(
                    title="Request Error",
                    message="Failed to submit consultation request",
                    details="There was an error submitting your request. Please try again."
                )
                return
                
            # Publish via MQTT for real-time notification
            mqtt_payload = {
                'request_id': request_id,
                'student_id': self.student.get('id'),
                'student_name': self.student.get('name'),
                'topic': request_data['topic'],
                'timestamp': datetime.now().isoformat()
            }
            
            topic = f"faculty/{faculty.get('id')}/requests"
            self.mqtt_client.publish(topic, mqtt_payload, qos=1)
            
            # Add audit log
            self.db_manager.add_audit_log({
                'action': 'consultation_request',
                'user_id': self.student.get('id'),
                'details': f"Requested consultation with {faculty.get('name')} on {request_data['topic']}",
                'timestamp': datetime.now().isoformat()
            })
            
            # Emit signal
            self.request_submitted.emit(request_data)
            
            # Show success message
            show_info_dialog(
                title="Request Submitted",
                message="Your consultation request has been submitted successfully",
                details=f"You will be notified when {faculty.get('name')} responds to your request."
            )
            
            # Reset form
            self.reset_form()
            
        except Exception as e:
            self.logger.error(f"Error submitting consultation request: {e}")
            show_error_dialog(
                title="Request Error",
                message="Failed to submit consultation request",
                details=str(e)
            ) 