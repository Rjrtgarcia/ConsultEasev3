#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Notification Handler

This module provides a notification handler to display real-time notifications.
"""

import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QIcon, QFont

from utils.logger import get_logger

class NotificationItem(QFrame):
    """
    Notification item widget.
    
    Signals:
        closed (object): Emitted when notification is closed, with notification data
        action_clicked (object): Emitted when action button is clicked, with notification data
    """
    closed = pyqtSignal(object)
    action_clicked = pyqtSignal(object)
    
    def __init__(self, notification, parent=None):
        """
        Initialize the notification item.
        
        Args:
            notification (dict): Notification data
            parent: Parent widget
        """
        super().__init__(parent)
        self.notification = notification
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("margin: 5px; padding: 10px; border-radius: 5px;")
        
        # Set background color based on notification type
        notification_type = notification.get('type', 'info')
        if notification_type == 'success':
            self.setStyleSheet("background-color: #E6F7F5; border: 1px solid #4ECDC4; border-radius: 5px; padding: 10px;")
        elif notification_type == 'warning':
            self.setStyleSheet("background-color: #FFF8E6; border: 1px solid #FFD166; border-radius: 5px; padding: 10px;")
        elif notification_type == 'error':
            self.setStyleSheet("background-color: #FFEDED; border: 1px solid #FF6B6B; border-radius: 5px; padding: 10px;")
        else:  # info
            self.setStyleSheet("background-color: #F0F4F8; border: 1px solid #C5D5E4; border-radius: 5px; padding: 10px;")
            
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header layout
        header_layout = QHBoxLayout()
        
        # Title
        title = self.notification.get('title', 'Notification')
        title_label = QLabel(f"<b>{title}</b>")
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Timestamp
        timestamp = self.notification.get('timestamp')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime('%H:%M')
                time_label = QLabel(time_str)
                time_label.setStyleSheet("color: #888;")
                header_layout.addWidget(time_label)
            except:
                pass
        
        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("background: transparent; border: none; font-size: 16px; color: #888;")
        close_button.clicked.connect(self.handle_close)
        header_layout.addWidget(close_button)
        
        layout.addLayout(header_layout)
        
        # Message
        message = self.notification.get('message', '')
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Action button (if available)
        action = self.notification.get('action')
        if action:
            action_layout = QHBoxLayout()
            action_layout.addStretch()
            
            action_button = QPushButton(action.get('text', 'View'))
            action_button.clicked.connect(self.handle_action)
            action_layout.addWidget(action_button)
            
            layout.addLayout(action_layout)
            
    def handle_close(self):
        """Handle close button click."""
        self.closed.emit(self.notification)
        
    def handle_action(self):
        """Handle action button click."""
        self.action_clicked.emit(self.notification)
        
class NotificationPanel(QWidget):
    """
    Panel for displaying notifications.
    
    Signals:
        notification_action (object): Emitted when a notification action is clicked
    """
    notification_action = pyqtSignal(object)
    
    def __init__(self, parent=None):
        """
        Initialize the notification panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        
        # Notification list
        self.notifications = []
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("Notifications")
        title_label.setStyleSheet("font-weight: bold;")
        title_layout.addWidget(title_label)
        
        # Clear all button
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_notifications)
        title_layout.addWidget(clear_button)
        
        main_layout.addLayout(title_layout)
        
        # Scroll area for notifications
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Container for notifications
        self.notification_container = QWidget()
        self.notification_layout = QVBoxLayout(self.notification_container)
        self.notification_layout.setContentsMargins(0, 0, 0, 0)
        self.notification_layout.setSpacing(5)
        self.notification_layout.addStretch()
        
        scroll_area.setWidget(self.notification_container)
        main_layout.addWidget(scroll_area)
        
    def add_notification(self, notification):
        """
        Add a notification to the panel.
        
        Args:
            notification (dict): Notification data including:
                - title: Notification title
                - message: Notification message
                - type: 'info', 'success', 'warning', or 'error'
                - timestamp: ISO format timestamp
                - action: Optional action object with 'text' and 'data'
                - data: Optional data associated with the notification
        """
        try:
            # Create notification item
            notification_item = NotificationItem(notification)
            notification_item.closed.connect(self.remove_notification)
            notification_item.action_clicked.connect(self.handle_notification_action)
            
            # Add to layout (before the stretch)
            self.notification_layout.insertWidget(self.notification_layout.count() - 1, notification_item)
            
            # Add to list
            self.notifications.append({
                'data': notification,
                'widget': notification_item
            })
            
            # Log notification
            self.logger.info(f"Added notification: {notification.get('title')}")
            
        except Exception as e:
            self.logger.error(f"Error adding notification: {e}")
            
    def remove_notification(self, notification):
        """
        Remove a notification from the panel.
        
        Args:
            notification (dict): Notification data
        """
        try:
            for item in self.notifications[:]:
                if item['data'] == notification:
                    # Remove widget
                    item['widget'].setParent(None)
                    item['widget'].deleteLater()
                    
                    # Remove from list
                    self.notifications.remove(item)
                    break
                    
        except Exception as e:
            self.logger.error(f"Error removing notification: {e}")
            
    def clear_notifications(self):
        """Clear all notifications."""
        try:
            for item in self.notifications[:]:
                # Remove widget
                item['widget'].setParent(None)
                item['widget'].deleteLater()
                
            # Clear list
            self.notifications.clear()
            
            self.logger.info("Cleared all notifications")
            
        except Exception as e:
            self.logger.error(f"Error clearing notifications: {e}")
            
    def handle_notification_action(self, notification):
        """
        Handle notification action click.
        
        Args:
            notification (dict): Notification data
        """
        # Emit signal with notification data
        self.notification_action.emit(notification)
        
class NotificationHandler:
    """
    Handler for system notifications.
    
    Manages notifications and connects to appropriate data sources.
    """
    
    def __init__(self, db_manager, mqtt_client, notification_panel):
        """
        Initialize the notification handler.
        
        Args:
            db_manager: Database manager instance
            mqtt_client: MQTT client instance
            notification_panel (NotificationPanel): Notification panel instance
        """
        self.logger = get_logger(__name__)
        self.db_manager = db_manager
        self.mqtt_client = mqtt_client
        self.notification_panel = notification_panel
        
        # Connect to MQTT signals
        if mqtt_client:
            mqtt_client.message_received.connect(self.handle_mqtt_message)
            mqtt_client.faculty_status_changed.connect(self.handle_faculty_status)
            mqtt_client.request_received.connect(self.handle_request)
            mqtt_client.request_updated.connect(self.handle_request_update)
            
    def handle_mqtt_message(self, topic, payload):
        """
        Handle MQTT message.
        
        Args:
            topic (str): Message topic
            payload (str): Message payload
        """
        try:
            # Parse the payload if it's JSON
            data = None
            try:
                data = json.loads(payload)
            except:
                data = {'message': payload}
                
            # Handle different topic patterns
            if 'notifications' in topic:
                # System notifications
                self.show_notification(
                    title=data.get('title', 'System Notification'),
                    message=data.get('message', payload),
                    notification_type=data.get('type', 'info'),
                    data=data
                )
                
        except Exception as e:
            self.logger.error(f"Error handling MQTT message: {e}")
            
    def handle_faculty_status(self, faculty_id, status):
        """
        Handle faculty status change.
        
        Args:
            faculty_id (str): Faculty ID
            status (str): New status
        """
        try:
            # Get faculty data
            faculty = self.db_manager.get_faculty_by_id(faculty_id)
            
            if faculty:
                faculty_name = faculty.get('name', 'Faculty')
                
                # Show notification based on status
                if status == 'available':
                    self.show_notification(
                        title="Faculty Available",
                        message=f"{faculty_name} is now available for consultations.",
                        notification_type="success",
                        data={'faculty_id': faculty_id, 'status': status}
                    )
                elif status == 'busy':
                    self.show_notification(
                        title="Faculty Busy",
                        message=f"{faculty_name} is now busy with a consultation.",
                        notification_type="warning",
                        data={'faculty_id': faculty_id, 'status': status}
                    )
                elif status == 'unavailable':
                    self.show_notification(
                        title="Faculty Unavailable",
                        message=f"{faculty_name} is no longer available for consultations.",
                        notification_type="info",
                        data={'faculty_id': faculty_id, 'status': status}
                    )
                    
        except Exception as e:
            self.logger.error(f"Error handling faculty status: {e}")
            
    def handle_request(self, request):
        """
        Handle incoming consultation request.
        
        Args:
            request (dict): Request data
        """
        try:
            student_name = request.get('student_name', 'A student')
            topic = request.get('topic', 'consultation')
            
            self.show_notification(
                title="New Consultation Request",
                message=f"{student_name} has requested a consultation about {topic}",
                notification_type="info",
                action={
                    'text': 'View',
                    'data': {'request_id': request.get('request_id')}
                },
                data=request
            )
            
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            
    def handle_request_update(self, request):
        """
        Handle consultation request update.
        
        Args:
            request (dict): Updated request data
        """
        try:
            request_id = request.get('request_id')
            status = request.get('status')
            faculty_name = request.get('faculty_name', 'Faculty')
            
            if status == 'acknowledged':
                self.show_notification(
                    title="Request Acknowledged",
                    message=f"{faculty_name} has acknowledged your consultation request",
                    notification_type="success",
                    action={
                        'text': 'View Details',
                        'data': {'request_id': request_id}
                    },
                    data=request
                )
            elif status == 'completed':
                self.show_notification(
                    title="Consultation Completed",
                    message=f"Your consultation with {faculty_name} has been marked as completed",
                    notification_type="success",
                    data=request
                )
            elif status == 'cancelled':
                self.show_notification(
                    title="Request Cancelled",
                    message=f"Your consultation request with {faculty_name} has been cancelled",
                    notification_type="warning",
                    data=request
                )
                
        except Exception as e:
            self.logger.error(f"Error handling request update: {e}")
            
    def show_notification(self, title, message, notification_type='info', action=None, data=None):
        """
        Show a notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            notification_type (str): 'info', 'success', 'warning', or 'error'
            action (dict, optional): Action data with 'text' and 'data'
            data (dict, optional): Additional data for the notification
        """
        # Create notification data
        notification = {
            'title': title,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'data': data
        }
        
        # Add to panel
        self.notification_panel.add_notification(notification) 