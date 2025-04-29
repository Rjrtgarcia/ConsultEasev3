#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Faculty Model

This module provides the Faculty model class for the ConsultEase application.
The Faculty class represents a faculty member and provides methods for data handling.
"""

from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from utils.logger import get_logger

class Faculty(QObject):
    """
    Faculty model class.
    
    Signals:
        data_changed (str): Emitted when faculty data changes with the name of the changed property
        status_changed (str): Emitted when faculty status changes with the new status
    """
    data_changed = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self, faculty_id=None, name=None, department=None, email=None, 
                 phone=None, office=None, ble_beacon_id=None, status="unavailable"):
        """
        Initialize a faculty member.
        
        Args:
            faculty_id (str, optional): Faculty ID
            name (str, optional): Faculty name
            department (str, optional): Department
            email (str, optional): Email address
            phone (str, optional): Phone number
            office (str, optional): Office location
            ble_beacon_id (str, optional): BLE beacon ID for presence detection
            status (str, optional): Current status ('available' or 'unavailable')
        """
        super().__init__()
        self.logger = get_logger(__name__)
        
        self._faculty_id = faculty_id
        self._name = name
        self._department = department
        self._email = email
        self._phone = phone
        self._office = office
        self._ble_beacon_id = ble_beacon_id
        self._status = status
        self._last_updated = datetime.now().isoformat()
        self._status_history = []
        
        # Initialize status history with current status
        self._add_status_history(status)
        
    def _add_status_history(self, status, reason=None):
        """
        Add a status change to the history.
        
        Args:
            status (str): New status
            reason (str, optional): Reason for the status change
        """
        entry = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'reason': reason
        }
        self._status_history.append(entry)
        
        # Limit history size to avoid excessive memory usage
        if len(self._status_history) > 100:
            self._status_history = self._status_history[-100:]
        
    @property
    def faculty_id(self):
        """Get faculty ID."""
        return self._faculty_id
        
    @faculty_id.setter
    def faculty_id(self, value):
        """Set faculty ID."""
        if self._faculty_id != value:
            self._faculty_id = value
            self.data_changed.emit('faculty_id')
        
    @property
    def name(self):
        """Get faculty name."""
        return self._name
        
    @name.setter
    def name(self, value):
        """Set faculty name."""
        if self._name != value:
            self._name = value
            self.data_changed.emit('name')
        
    @property
    def department(self):
        """Get department."""
        return self._department
        
    @department.setter
    def department(self, value):
        """Set department."""
        if self._department != value:
            self._department = value
            self.data_changed.emit('department')
        
    @property
    def email(self):
        """Get email address."""
        return self._email
        
    @email.setter
    def email(self, value):
        """Set email address."""
        if self._email != value:
            self._email = value
            self.data_changed.emit('email')
        
    @property
    def phone(self):
        """Get phone number."""
        return self._phone
        
    @phone.setter
    def phone(self, value):
        """Set phone number."""
        if self._phone != value:
            self._phone = value
            self.data_changed.emit('phone')
        
    @property
    def office(self):
        """Get office location."""
        return self._office
        
    @office.setter
    def office(self, value):
        """Set office location."""
        if self._office != value:
            self._office = value
            self.data_changed.emit('office')
        
    @property
    def ble_beacon_id(self):
        """Get BLE beacon ID."""
        return self._ble_beacon_id
        
    @ble_beacon_id.setter
    def ble_beacon_id(self, value):
        """Set BLE beacon ID."""
        if self._ble_beacon_id != value:
            self._ble_beacon_id = value
            self.data_changed.emit('ble_beacon_id')
        
    @property
    def status(self):
        """Get current status."""
        return self._status
        
    @status.setter
    def status(self, value, reason=None):
        """
        Set current status.
        
        Args:
            value (str): New status value
            reason (str, optional): Reason for the status change
        """
        if value not in ['available', 'unavailable', 'busy']:
            raise ValueError(f"Invalid status: {value}")
            
        if self._status != value:
            old_status = self._status
            self._status = value
            self._last_updated = datetime.now().isoformat()
            
            # Add to status history
            self._add_status_history(value, reason)
            
            self.data_changed.emit('status')
            self.status_changed.emit(value)
            self.logger.info(f"Faculty {self.name} ({self.faculty_id}) status changed from {old_status} to {value}")
            
    @property
    def last_updated(self):
        """Get last updated timestamp."""
        return self._last_updated
        
    @property
    def status_history(self):
        """Get status change history."""
        return self._status_history.copy()
        
    def get_history_since(self, timestamp):
        """
        Get status history since a specific timestamp.
        
        Args:
            timestamp (str): ISO format timestamp
            
        Returns:
            list: Status history entries since the timestamp
        """
        if not timestamp:
            return self.status_history
            
        return [entry for entry in self._status_history if entry['timestamp'] > timestamp]
        
    def to_dict(self):
        """
        Convert faculty member to dictionary.
        
        Returns:
            dict: Faculty data as dictionary
        """
        return {
            'id': self._faculty_id,
            'name': self._name,
            'department': self._department,
            'email': self._email,
            'phone': self._phone,
            'office': self._office,
            'ble_beacon_id': self._ble_beacon_id,
            'status': self._status,
            'last_updated': self._last_updated,
            'status_history': self._status_history
        }
        
    @classmethod
    def from_dict(cls, data):
        """
        Create a faculty member from dictionary.
        
        Args:
            data (dict): Faculty data as dictionary
            
        Returns:
            Faculty: Faculty instance
        """
        faculty = cls(
            faculty_id=data.get('id'),
            name=data.get('name'),
            department=data.get('department'),
            email=data.get('email'),
            phone=data.get('phone'),
            office=data.get('office'),
            ble_beacon_id=data.get('ble_beacon_id'),
            status=data.get('status', 'unavailable')
        )
        
        if 'last_updated' in data:
            faculty._last_updated = data['last_updated']
            
        if 'status_history' in data and isinstance(data['status_history'], list):
            faculty._status_history = data['status_history']
            
        return faculty
        
    def __str__(self):
        """String representation of faculty member."""
        return f"Faculty(id={self._faculty_id}, name={self._name}, status={self._status})"
