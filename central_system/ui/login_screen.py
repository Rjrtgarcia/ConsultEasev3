#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Login Screen

This module provides the login screen for the ConsultEase application.
It handles RFID authentication and manual login.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QLineEdit, QGroupBox, QFormLayout, QMessageBox,
                            QSizePolicy, QSpacerItem, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon

from hardware.rfid_reader import HybridRFIDReader
from ui.main_dashboard import MainDashboard
from ui.admin_interface import AdminInterface
from utils.logger import get_logger
from utils.error_handler import show_error_dialog, show_warning_dialog
from data.models import Student

class LoginScreen(QWidget):
    """
    Login screen for the ConsultEase application.
    Handles RFID authentication and manual login.
    """
    
    def __init__(self, db_manager, mqtt_client):
        """
        Initialize the login screen.
        
        Args:
            db_manager: Database manager instance
            mqtt_client: MQTT client instance
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.mqtt_client = mqtt_client
        
        # Initialize RFID reader
        self.rfid_reader = HybridRFIDReader(self)
        self.rfid_reader.card_detected.connect(self.handle_rfid_scan)
        self.rfid_reader.status_changed.connect(self.update_rfid_status)
        self.rfid_reader.error_occurred.connect(self.handle_rfid_error)
        self.rfid_reader.reader_detected.connect(self.handle_reader_detected)
        
        # Initialize UI
        self.init_ui()
        
        # Start RFID detection
        self.rfid_reader.start_detection()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("ConsultEase - Login")
        self.setMinimumSize(800, 600)
        
        # Check if touchscreen mode is enabled
        is_touchscreen = os.getenv("TOUCHSCREEN_ENABLED", "False").lower() == "true"
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Logo (placeholder)
        logo_size = 120 if is_touchscreen else 64
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "assets", "logo.png")
        
        # Create logo label regardless of whether the image exists
        logo_label = QLabel()
        logo_label.setObjectName("logo")
        
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(logo_size, logo_size, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            # If logo image doesn't exist, set a text placeholder
            logo_label.setText("CE")
            logo_label.setStyleSheet("background-color: #4ECDC4; color: #121212; font-weight: bold; border-radius: 32px;")
            logo_label.setFixedSize(logo_size, logo_size)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        header_layout.addWidget(logo_label)
        
        logo_text = QLabel("ConsultEase")
        logo_text.setObjectName("logo-label")
        font_size = 28 if is_touchscreen else 24
        logo_text.setFont(QFont("Roboto", font_size, QFont.Weight.Bold))
        header_layout.addWidget(logo_text)
        
        # Spacer
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # RFID status
        self.rfid_status_label = QLabel("RFID Status: Initializing...")
        self.rfid_status_label.setObjectName("rfid-status")
        header_layout.addWidget(self.rfid_status_label)
        
        main_layout.addLayout(header_layout)
        
        # RFID scan area
        scan_frame = QFrame()
        scan_frame.setObjectName("scan-frame")
        scan_frame.setFrameShape(QFrame.Shape.StyledPanel)
        scan_frame.setFrameShadow(QFrame.Shadow.Raised)
        scan_frame.setMinimumHeight(200)
        
        scan_layout = QVBoxLayout(scan_frame)
        scan_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # RFID icon
        rfid_icon = QLabel()
        rfid_icon.setObjectName("rfid-icon")
        rfid_icon.setMinimumSize(64, 64)
        rfid_icon.setMaximumSize(64, 64)
        rfid_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Try to load RFID icon
        rfid_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "assets", "rfid.png")
        if os.path.exists(rfid_icon_path):
            rfid_pixmap = QPixmap(rfid_icon_path)
            rfid_icon.setPixmap(rfid_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        
        scan_layout.addWidget(rfid_icon, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Scan prompt
        scan_prompt_font_size = 18 if is_touchscreen else 16
        self.scan_prompt = QLabel("Please scan your RFID card")
        self.scan_prompt.setObjectName("scan-prompt")
        self.scan_prompt.setFont(QFont("Roboto", scan_prompt_font_size))
        self.scan_prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scan_layout.addWidget(self.scan_prompt)
        
        # Status indicator
        self.status_indicator = QLabel("")
        self.status_indicator.setObjectName("status-neutral")
        self.status_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scan_layout.addWidget(self.status_indicator)
        
        main_layout.addWidget(scan_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        button_height = 48 if is_touchscreen else 40
        
        # Manual login button
        self.manual_button = QPushButton("Manual Login")
        self.manual_button.setObjectName("secondary-button")
        self.manual_button.setMinimumHeight(button_height)
        self.manual_button.clicked.connect(self.show_manual_login)
        buttons_layout.addWidget(self.manual_button)
        
        # Admin login button
        self.admin_button = QPushButton("Admin Login")
        self.admin_button.setObjectName("text-button")
        self.admin_button.setMinimumHeight(button_height)
        self.admin_button.clicked.connect(self.show_admin_login)
        buttons_layout.addWidget(self.admin_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Simulation controls (initially hidden)
        self.sim_frame = None
        
        # Set main layout
        self.setLayout(main_layout)
        
        # Apply touchscreen optimizations if needed
        if is_touchscreen:
            self.apply_touchscreen_optimizations()
        
    def apply_touchscreen_optimizations(self):
        """Apply optimizations for touchscreen display."""
        # Increase spacing for touch targets
        self.layout().setSpacing(30)
        self.layout().setContentsMargins(30, 30, 30, 30)
        
        # Increase button sizes
        for button in self.findChildren(QPushButton):
            button.setMinimumHeight(60)
            button.setMinimumWidth(200)
        
    def init_simulation_controls(self):
        """Initialize simulation controls for RFID reader."""
        if self.sim_frame:
            return
            
        self.logger.info("Initializing simulation controls")
        
        # Create simulation frame
        self.sim_frame = QGroupBox("RFID Simulation Mode")
        self.sim_frame.setObjectName("simulation-frame")
        
        sim_layout = QFormLayout(self.sim_frame)
        
        # RFID input field
        self.sim_id_input = QLineEdit()
        self.sim_id_input.setPlaceholderText("Enter RFID ID to simulate (e.g., A1B2C3D4)")
        sim_layout.addRow("RFID ID:", self.sim_id_input)
        
        # Simulate button
        sim_button = QPushButton("Simulate Scan")
        sim_button.setObjectName("primary-button")
        sim_button.clicked.connect(self.simulate_rfid_scan)
        sim_layout.addRow("", sim_button)
        
        # Sample IDs
        sample_label = QLabel("Sample IDs: A1B2C3D4 (Alice), E5F6G7H8 (Bob), I9J0K1L2 (Charlie)")
        sample_label.setObjectName("help-text")
        sim_layout.addRow("", sample_label)
        
        # Add to main layout
        self.layout().addWidget(self.sim_frame)
        
    def update_rfid_status(self, status):
        """
        Update the RFID status label.
        
        Args:
            status (str): Status message
        """
        self.rfid_status_label.setText(f"RFID Status: {status}")
        
        # Initialize simulation controls if in simulation mode
        if "simulation" in status.lower():
            self.init_simulation_controls()
            
    def handle_rfid_scan(self, rfid_id):
        """
        Handle RFID card detection.
        
        Args:
            rfid_id (str): RFID card ID
        """
        self.logger.info(f"RFID card scanned: {rfid_id}")
        
        # Update UI to show scanning in progress
        self.status_indicator.setObjectName("status-processing")
        self.status_indicator.setText("Processing RFID...")
        self.status_indicator.setStyleSheet("color: #FFD166;")  # Amber color
        # QApplication.processEvents()  # Force update UI - Removed for smoother event handling
        
        # Validate against database
        try:
            student_data = self.db_manager.get_student_by_rfid(rfid_id)
        
            if student_data:
                # Create student model
                student = Student.from_dict(student_data)
                student.record_login()
                
                # Update student in database
                self.db_manager.update_student(student.student_id, student.to_dict())
                
                # Valid student card
                self.status_indicator.setObjectName("status-success")
                self.status_indicator.setText(f"Welcome, {student.name}!")
                self.status_indicator.setStyleSheet("color: #4ECDC4;")  # Green color
                
                self.logger.info(f"Student authenticated: {student.student_id} ({student.name})")
                
                # Record login in audit log
                self.db_manager.add_audit_log({
                    'action': 'student_login',
                    'user_id': student.student_id,
                    'details': f"Student login via RFID",
                    'timestamp': datetime.now().isoformat()
                })
                
                # Wait a moment, then proceed to main dashboard
                QTimer.singleShot(1500, lambda: self.show_dashboard(student))
            else:
                # Invalid card
                self.status_indicator.setObjectName("status-error")
                self.status_indicator.setText("Unknown RFID card. Please try again.")
                self.status_indicator.setStyleSheet("color: #FF6B6B;")  # Red color
                
                self.logger.warning(f"Unknown RFID card scanned: {rfid_id}")
        except Exception as e:
            self.logger.error(f"Error authenticating student: {e}")
            self.status_indicator.setObjectName("status-error")
            self.status_indicator.setText("Authentication error. Please try again.")
            self.status_indicator.setStyleSheet("color: #FF6B6B;")  # Red color
            
    def handle_rfid_error(self, error_message):
        """
        Handle RFID reader errors.
        
        Args:
            error_message (str): Error message
        """
        self.logger.error(f"RFID reader error: {error_message}")
        self.status_indicator.setObjectName("status-error")
        self.status_indicator.setText(f"RFID reader error. Please try again.")
        self.status_indicator.setStyleSheet("color: #FF6B6B;")  # Red color
        
    def simulate_rfid_scan(self):
        """Simulate an RFID card scan."""
        if not hasattr(self, 'sim_id_input') or not self.sim_id_input:
            self.logger.warning("Simulation controls not initialized")
            return
            
        rfid_id = self.sim_id_input.text().strip()
        if not rfid_id:
            show_warning_dialog(
                title="Empty Input",
                message="Please enter an RFID ID to simulate",
                details="The RFID ID field cannot be empty."
            )
            return
            
        # Simulate RFID scan
        self.rfid_reader.simulate_scan(rfid_id)
        
    def show_manual_login(self):
        """Show manual login dialog."""
        self.logger.info("Showing manual login dialog")
        
        # Create manual login dialog
        from ui.dialogs.manual_login_dialog import ManualLoginDialog
        dialog = ManualLoginDialog(self.db_manager, self)
        
        if dialog.exec():
            student = dialog.get_student()
            if student:
                self.show_dashboard(student)
        
    def show_admin_login(self):
        """Show admin login dialog."""
        self.logger.info("Showing admin login dialog")
        
        # Create admin login dialog
        from ui.dialogs.admin_login_dialog import AdminLoginDialog
        dialog = AdminLoginDialog(self.db_manager, self)
        
        if dialog.exec():
            admin_user = dialog.get_admin_user()
            if admin_user:
                self.show_admin_interface(admin_user)
        
    def show_dashboard(self, student):
        """
        Show the main dashboard.
        
        Args:
            student (Student): Student instance
        """
        self.logger.info(f"Showing dashboard for student: {student.student_id}")
        
        try:
            # Create dashboard
            dashboard = MainDashboard(self.db_manager, self.mqtt_client, student)
            dashboard.logout_requested.connect(self.show_login)
            
            # Hide login screen
            self.hide()
            
            # Show dashboard
            dashboard.showMaximized()
            
        except Exception as e:
            self.logger.error(f"Error showing dashboard: {e}")
            show_error_dialog(
                title="Dashboard Error",
                message="Failed to open the dashboard",
                details=str(e)
            )
            
    def show_admin_interface(self, admin_user):
        """
        Show the admin interface.
        
        Args:
            admin_user (dict): Admin user data
        """
        self.logger.info(f"Showing admin interface for user: {admin_user.get('username')}")
        
        try:
            # Create admin interface
            admin = AdminInterface(self.db_manager, self.mqtt_client, admin_user)
            admin.logout_requested.connect(self.show_login)
        
            # Hide login screen
            self.hide()
        
            # Show admin interface
            admin.showMaximized()
            
        except Exception as e:
            self.logger.error(f"Error showing admin interface: {e}")
            show_error_dialog(
                title="Admin Interface Error",
                message="Failed to open the admin interface",
                details=str(e)
            )
            
    def show_login(self):
        """Show the login screen (callback for logout)."""
        self.logger.info("Returning to login screen")
        self.show()
        
        # Reset status indicator
        self.status_indicator.setText("")
        self.status_indicator.setObjectName("status-neutral")
        self.status_indicator.setStyleSheet("")
        
        # Resume RFID detection if needed
        if self.rfid_reader:
            self.rfid_reader.start_detection()
            
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        self.logger.info("Login screen closing")
        
        # Stop RFID detection
        if self.rfid_reader:
            self.rfid_reader.stop_detection()
        
        event.accept()

    def handle_reader_detected(self, reader_info):
        """
        Handle RFID reader detection.
        
        Args:
            reader_info (dict): Reader information
        """
        self.logger.info(f"RFID reader detected: {reader_info['name']}")
        
        # Update UI with reader information
        if hasattr(self, 'rfid_status_label'):
            self.rfid_status_label.setText(f"RFID Reader: {reader_info['name']}")
            self.rfid_status_label.setStyleSheet("color: #4ECDC4;")  # Green color
