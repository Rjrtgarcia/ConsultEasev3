#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Admin Interface

This module provides the admin interface for the ConsultEase application.
It allows administrators to manage faculty and student information,
view consultation requests, and system settings.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QLabel, QPushButton, QFrame, QStackedWidget,
                            QSplitter, QTreeWidget, QTreeWidgetItem, QMessageBox,
                            QMenu, QToolBar, QStatusBar, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QIcon, QAction, QFont

from utils.logger import get_logger
from utils.error_handler import show_error_dialog, show_confirmation_dialog
from data.models import Faculty, Student, ConsultationRequest
from ui.admin_panels.faculty_manager import FacultyManagerPanel
from ui.admin_panels.student_manager import StudentManagerPanel
from ui.admin_panels.request_manager import RequestManagerPanel
from ui.admin_panels.audit_log_viewer import AuditLogViewerPanel
from ui.admin_panels.system_settings import SystemSettingsPanel

class AdminInterface(QMainWindow):
    """
    Admin interface main window for ConsultEase.
    Provides access to all administrative functions.
    
    Signals:
        logout_requested: Emitted when the admin logs out
    """
    logout_requested = pyqtSignal()
    
    def __init__(self, db_manager, mqtt_client, admin_user):
        """
        Initialize the admin interface.
        
        Args:
            db_manager: Database manager instance
            mqtt_client: MQTT client instance
            admin_user (dict): Admin user data
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.mqtt_client = mqtt_client
        self.admin_user = admin_user
        
        self.init_ui()
        self.logger.info(f"Admin interface initialized for {admin_user.get('username')}")
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("ConsultEase - Administration")
        self.setMinimumSize(1024, 768)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = self.create_sidebar()
        
        # Create content area
        self.content_stack = QStackedWidget()
        
        # Create panels
        self.faculty_panel = FacultyManagerPanel(self.db_manager, self.mqtt_client)
        self.student_panel = StudentManagerPanel(self.db_manager)
        self.request_panel = RequestManagerPanel(self.db_manager, self.mqtt_client)
        self.audit_panel = AuditLogViewerPanel(self.db_manager)
        self.settings_panel = SystemSettingsPanel()
        
        # Add panels to stack
        self.content_stack.addWidget(self.faculty_panel)
        self.content_stack.addWidget(self.student_panel)
        self.content_stack.addWidget(self.request_panel)
        self.content_stack.addWidget(self.audit_panel)
        self.content_stack.addWidget(self.settings_panel)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.content_stack)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([200, 800])
        
        main_layout.addWidget(splitter)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage(f"Logged in as {self.admin_user.get('username')} | Role: {self.admin_user.get('role', 'Administrator')}")
        
    def create_sidebar(self):
        """
        Create the sidebar navigation.
        
        Returns:
            QWidget: Sidebar widget
        """
        sidebar = QWidget()
        sidebar.setObjectName("admin-sidebar")
        sidebar.setMinimumWidth(200)
        sidebar.setMaximumWidth(250)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Header
        header = QLabel("Admin Panel")
        header.setObjectName("admin-header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setMinimumHeight(50)
        header.setFont(QFont("Roboto", 16, QFont.Weight.Bold))
        sidebar_layout.addWidget(header)
        
        # Navigation buttons
        nav_frame = QFrame()
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(5)
        
        # Faculty button
        faculty_btn = QPushButton("Faculty Management")
        faculty_btn.setObjectName("nav-button")
        faculty_btn.setCheckable(True)
        faculty_btn.setChecked(True)
        faculty_btn.clicked.connect(lambda: self.switch_panel(0, faculty_btn))
        nav_layout.addWidget(faculty_btn)
        
        # Student button
        student_btn = QPushButton("Student Management")
        student_btn.setObjectName("nav-button")
        student_btn.setCheckable(True)
        student_btn.clicked.connect(lambda: self.switch_panel(1, student_btn))
        nav_layout.addWidget(student_btn)
        
        # Requests button
        requests_btn = QPushButton("Consultation Requests")
        requests_btn.setObjectName("nav-button")
        requests_btn.setCheckable(True)
        requests_btn.clicked.connect(lambda: self.switch_panel(2, requests_btn))
        nav_layout.addWidget(requests_btn)
        
        # Audit logs button
        audit_btn = QPushButton("Audit Logs")
        audit_btn.setObjectName("nav-button")
        audit_btn.setCheckable(True)
        audit_btn.clicked.connect(lambda: self.switch_panel(3, audit_btn))
        nav_layout.addWidget(audit_btn)
        
        # Settings button
        settings_btn = QPushButton("System Settings")
        settings_btn.setObjectName("nav-button")
        settings_btn.setCheckable(True)
        settings_btn.clicked.connect(lambda: self.switch_panel(4, settings_btn))
        nav_layout.addWidget(settings_btn)
        
        # Store navigation buttons for state management
        self.nav_buttons = [faculty_btn, student_btn, requests_btn, audit_btn, settings_btn]
        
        sidebar_layout.addWidget(nav_frame)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sidebar_layout.addWidget(spacer)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("secondary-button")
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        return sidebar
        
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Refresh action
        refresh_action = QAction("Refresh", self)
        refresh_action.setStatusTip("Refresh current data")
        refresh_action.triggered.connect(self.refresh_current_panel)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Admin info
        admin_label = QLabel(f"Admin: {self.admin_user.get('username')}")
        admin_label.setStyleSheet("padding: 0 10px;")
        toolbar.addWidget(admin_label)
        
    def switch_panel(self, index, button=None):
        """
        Switch to the specified panel.
        
        Args:
            index (int): Panel index
            button (QPushButton, optional): Button that was clicked
        """
        # Update button states
        if button:
            for btn in self.nav_buttons:
                if btn != button:
                    btn.setChecked(False)
            button.setChecked(True)
        
        # Switch panel
        self.content_stack.setCurrentIndex(index)
        
        # Refresh the panel data
        self.refresh_current_panel()
        
    def refresh_current_panel(self):
        """Refresh the current panel's data."""
        current_panel = self.content_stack.currentWidget()
        if hasattr(current_panel, 'refresh_data'):
            current_panel.refresh_data()
        
    def logout(self):
        """Handle admin logout."""
        if show_confirmation_dialog(
            title="Confirm Logout",
            message="Are you sure you want to logout?",
            details="Any unsaved changes will be lost."
        ):
            self.logger.info(f"Admin logout: {self.admin_user.get('username')}")
            
            # Log the admin logout
            self.db_manager.add_audit_log({
                'action': 'admin_logout',
                'user_id': self.admin_user.get('id'),
                'username': self.admin_user.get('username'),
                'details': "Admin logout"
            })
            
            # Emit logout signal
            self.logout_requested.emit()
            
            # Close the window
            self.close()
            
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        # Emit logout signal if not already emitted
        self.logout_requested.emit()
        event.accept()
