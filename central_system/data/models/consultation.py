#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Consultation Request Model

This module provides the ConsultationRequest model class for the ConsultEase application.
"""

from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal

class ConsultationRequest(QObject):
    """
    Consultation request model class.
    
    Signals:
        status_changed (str): Emitted when the request status changes
        data_changed: Emitted when any request data changes
    """
    status_changed = pyqtSignal(str)
    data_changed = pyqtSignal()
    
    # Status constants
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    
    def __init__(self, request_id=None, student_id=None, faculty_id=None, 
                 request_text=None, course_code=None, status=STATUS_PENDING):
        """
        Initialize a consultation request.
        
        Args:
            request_id (str, optional): Request ID
            student_id (str, optional): Student ID
            faculty_id (str, optional): Faculty ID
            request_text (str, optional): Request text
            course_code (str, optional): Course code
            status (str, optional): Request status
        """
        super().__init__()
        self._id = request_id
        self._student_id = student_id
        self._faculty_id = faculty_id
        self._request_text = request_text
        self._course_code = course_code
        self._status = status
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        
    @property
    def id(self):
        """Get request ID."""
        return self._id
        
    @id.setter
    def id(self, value):
        """Set request ID."""
        self._id = value
        self.data_changed.emit()
        
    @property
    def student_id(self):
        """Get student ID."""
        return self._student_id
        
    @student_id.setter
    def student_id(self, value):
        """Set student ID."""
        self._student_id = value
        self.data_changed.emit()
        
    @property
    def faculty_id(self):
        """Get faculty ID."""
        return self._faculty_id
        
    @faculty_id.setter
    def faculty_id(self, value):
        """Set faculty ID."""
        self._faculty_id = value
        self.data_changed.emit()
        
    @property
    def request_text(self):
        """Get request text."""
        return self._request_text
        
    @request_text.setter
    def request_text(self, value):
        """Set request text."""
        self._request_text = value
        self._updated_at = datetime.now()
        self.data_changed.emit()
        
    @property
    def course_code(self):
        """Get course code."""
        return self._course_code
        
    @course_code.setter
    def course_code(self, value):
        """Set course code."""
        self._course_code = value
        self._updated_at = datetime.now()
        self.data_changed.emit()
        
    @property
    def status(self):
        """Get request status."""
        return self._status
        
    @status.setter
    def status(self, value):
        """Set request status."""
        if value != self._status:
            old_status = self._status
            self._status = value
            self._updated_at = datetime.now()
            self.status_changed.emit(value)
            self.data_changed.emit()
            
    @property
    def created_at(self):
        """Get creation timestamp."""
        return self._created_at
        
    @created_at.setter
    def created_at(self, value):
        """Set creation timestamp."""
        self._created_at = value
        
    @property
    def updated_at(self):
        """Get update timestamp."""
        return self._updated_at
        
    @updated_at.setter
    def updated_at(self, value):
        """Set update timestamp."""
        self._updated_at = value
        
    def accept(self):
        """Accept the consultation request."""
        self.status = self.STATUS_ACCEPTED
        
    def complete(self):
        """Mark the consultation request as completed."""
        self.status = self.STATUS_COMPLETED
        
    def cancel(self):
        """Cancel the consultation request."""
        self.status = self.STATUS_CANCELLED
        
    def to_dict(self):
        """
        Convert consultation request to dictionary.
        
        Returns:
            dict: Consultation request data as dictionary
        """
        return {
            'id': self._id,
            'student_id': self._student_id,
            'faculty_id': self._faculty_id,
            'request_text': self._request_text,
            'course_code': self._course_code,
            'status': self._status,
            'created_at': self._created_at.isoformat() if isinstance(self._created_at, datetime) else self._created_at,
            'updated_at': self._updated_at.isoformat() if isinstance(self._updated_at, datetime) else self._updated_at
        }
        
    @classmethod
    def from_dict(cls, data):
        """
        Create consultation request from dictionary.
        
        Args:
            data (dict): Consultation request data
            
        Returns:
            ConsultationRequest: ConsultationRequest instance
        """
        request = cls()
        
        request._id = data.get('id')
        request._student_id = data.get('student_id')
        request._faculty_id = data.get('faculty_id')
        request._request_text = data.get('request_text')
        request._course_code = data.get('course_code')
        request._status = data.get('status', cls.STATUS_PENDING)
        
        # Parse timestamps
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                request._created_at = datetime.fromisoformat(created_at)
            except ValueError:
                request._created_at = datetime.now()
        else:
            request._created_at = created_at or datetime.now()
            
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            try:
                request._updated_at = datetime.fromisoformat(updated_at)
            except ValueError:
                request._updated_at = datetime.now()
        else:
            request._updated_at = updated_at or datetime.now()
            
        return request
        
    def __str__(self):
        """String representation of consultation request."""
        return f"Request {self._id}: {self._status}"
