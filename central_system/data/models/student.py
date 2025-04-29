#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Student Model

This module provides the Student model class for the ConsultEase application.
The Student class represents a student and provides methods for data handling.
"""

from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from utils.logger import get_logger

class Student(QObject):
    """
    Student model class.
    
    Signals:
        data_changed (str): Emitted when student data changes with the name of the changed property
    """
    data_changed = pyqtSignal(str)
    
    def __init__(self, student_id=None, rfid_id=None, name=None, department=None, email=None):
        """
        Initialize a student.
        
        Args:
            student_id (str, optional): Student ID
            rfid_id (str, optional): RFID card ID
            name (str, optional): Student name
            department (str, optional): Department
            email (str, optional): Email address
        """
        super().__init__()
        self.logger = get_logger(__name__)
        
        self._student_id = student_id
        self._rfid_id = rfid_id
        self._name = name
        self._department = department
        self._email = email
        self._created_at = datetime.now().isoformat()
        self._last_login = None
        
    @property
    def student_id(self):
        """Get student ID."""
        return self._student_id
        
    @student_id.setter
    def student_id(self, value):
        """Set student ID."""
        if self._student_id != value:
            self._student_id = value
            self.data_changed.emit('student_id')
            
    @property
    def rfid_id(self):
        """Get RFID card ID."""
        return self._rfid_id
        
    @rfid_id.setter
    def rfid_id(self, value):
        """Set RFID card ID."""
        if self._rfid_id != value:
            self._rfid_id = value
            self.data_changed.emit('rfid_id')
            
    @property
    def name(self):
        """Get student name."""
        return self._name
        
    @name.setter
    def name(self, value):
        """Set student name."""
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
    def created_at(self):
        """Get creation timestamp."""
        return self._created_at
        
    @property
    def last_login(self):
        """Get last login timestamp."""
        return self._last_login
        
    @last_login.setter
    def last_login(self, value):
        """Set last login timestamp."""
        self._last_login = value
        self.data_changed.emit('last_login')
        
    def record_login(self):
        """Record login event."""
        self._last_login = datetime.now().isoformat()
        self.data_changed.emit('last_login')
        self.logger.info(f"Student login recorded for {self.name} ({self.student_id})")
        
    def to_dict(self):
        """
        Convert student to dictionary.
        
        Returns:
            dict: Student data as dictionary
        """
        return {
            'id': self._student_id,
            'rfid_id': self._rfid_id,
            'name': self._name,
            'department': self._department,
            'email': self._email,
            'created_at': self._created_at,
            'last_login': self._last_login
        }
        
    @classmethod
    def from_dict(cls, data):
        """
        Create a student from dictionary.
        
        Args:
            data (dict): Student data as dictionary
            
        Returns:
            Student: Student instance
        """
        student = cls(
            student_id=data.get('id'),
            rfid_id=data.get('rfid_id'),
            name=data.get('name'),
            department=data.get('department'),
            email=data.get('email')
        )
        
        if 'created_at' in data:
            student._created_at = data['created_at']
            
        if 'last_login' in data:
            student._last_login = data['last_login']
            
        return student
        
    def __str__(self):
        """String representation of student."""
        return f"Student(id={self._student_id}, name={self._name}, rfid={self._rfid_id})"
