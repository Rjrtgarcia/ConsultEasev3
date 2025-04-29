#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Consultation Request Model

This module provides the ConsultationRequest model class for the ConsultEase application.
The ConsultationRequest class represents a student's request to consult with a faculty member.
"""

import uuid
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from utils.logger import get_logger

class ConsultationRequest(QObject):
    """
    Consultation request model class.
    
    Signals:
        data_changed (str): Emitted when request data changes with the name of the changed property
        status_changed (str): Emitted when request status changes with the new status
    """
    data_changed = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    # Valid status values
    STATUSES = ['pending', 'accepted', 'rejected', 'completed', 'cancelled']
    
    def __init__(self, request_id=None, student_id=None, faculty_id=None,
                 request_text=None, course_code=None, status='pending'):
        """
        Initialize a consultation request.
        
        Args:
            request_id (str, optional): Request ID
            student_id (str, optional): Student ID
            faculty_id (str, optional): Faculty ID
            request_text (str, optional): Request description
            course_code (str, optional): Course code
            status (str, optional): Request status
        """
        super().__init__()
        self.logger = get_logger(__name__)
        
        self._request_id = request_id or str(uuid.uuid4())
        self._student_id = student_id
        self._faculty_id = faculty_id
        self._request_text = request_text
        self._course_code = course_code
        self._status = status
        self._created_at = datetime.now().isoformat()
        self._updated_at = self._created_at
        self._completed_at = None
        
    @property
    def request_id(self):
        """Get request ID."""
        return self._request_id
        
    @property
    def student_id(self):
        """Get student ID."""
        return self._student_id
        
    @student_id.setter
    def student_id(self, value):
        """Set student ID."""
        if self._student_id != value:
            self._student_id = value
            self._updated_at = datetime.now().isoformat()
            self.data_changed.emit('student_id')
            
    @property
    def faculty_id(self):
        """Get faculty ID."""
        return self._faculty_id
        
    @faculty_id.setter
    def faculty_id(self, value):
        """Set faculty ID."""
        if self._faculty_id != value:
            self._faculty_id = value
            self._updated_at = datetime.now().isoformat()
            self.data_changed.emit('faculty_id')
            
    @property
    def request_text(self):
        """Get request text."""
        return self._request_text
        
    @request_text.setter
    def request_text(self, value):
        """Set request text."""
        if self._request_text != value:
            self._request_text = value
            self._updated_at = datetime.now().isoformat()
            self.data_changed.emit('request_text')
            
    @property
    def course_code(self):
        """Get course code."""
        return self._course_code
        
    @course_code.setter
    def course_code(self, value):
        """Set course code."""
        if self._course_code != value:
            self._course_code = value
            self._updated_at = datetime.now().isoformat()
            self.data_changed.emit('course_code')
            
    @property
    def status(self):
        """Get request status."""
        return self._status
        
    @status.setter
    def status(self, value):
        """Set request status."""
        if value not in self.STATUSES:
            raise ValueError(f"Invalid status: {value}. Must be one of {self.STATUSES}")
            
        if self._status != value:
            old_status = self._status
            self._status = value
            self._updated_at = datetime.now().isoformat()
            
            # If moving to completed status, record completion time
            if value == 'completed' and old_status != 'completed':
                self._completed_at = datetime.now().isoformat()
                
            self.data_changed.emit('status')
            self.status_changed.emit(value)
            self.logger.info(f"Request {self.request_id} status changed from {old_status} to {value}")
            
    @property
    def created_at(self):
        """Get creation timestamp."""
        return self._created_at
        
    @property
    def updated_at(self):
        """Get last update timestamp."""
        return self._updated_at
        
    @property
    def completed_at(self):
        """Get completion timestamp."""
        return self._completed_at
        
    def accept(self):
        """Accept the request."""
        self.status = 'accepted'
        
    def reject(self):
        """Reject the request."""
        self.status = 'rejected'
        
    def complete(self):
        """Mark the request as completed."""
        self.status = 'completed'
        
    def cancel(self):
        """Cancel the request."""
        self.status = 'cancelled'
        
    def to_dict(self):
        """
        Convert consultation request to dictionary.
        
        Returns:
            dict: Request data as dictionary
        """
        return {
            'id': self._request_id,
            'student_id': self._student_id,
            'faculty_id': self._faculty_id,
            'request_text': self._request_text,
            'course_code': self._course_code,
            'status': self._status,
            'created_at': self._created_at,
            'updated_at': self._updated_at,
            'completed_at': self._completed_at
        }
        
    @classmethod
    def from_dict(cls, data):
        """
        Create a consultation request from dictionary.
        
        Args:
            data (dict): Request data as dictionary
            
        Returns:
            ConsultationRequest: Consultation request instance
        """
        request = cls(
            request_id=data.get('id'),
            student_id=data.get('student_id'),
            faculty_id=data.get('faculty_id'),
            request_text=data.get('request_text'),
            course_code=data.get('course_code'),
            status=data.get('status', 'pending')
        )
        
        if 'created_at' in data:
            request._created_at = data['created_at']
            
        if 'updated_at' in data:
            request._updated_at = data['updated_at']
            
        if 'completed_at' in data:
            request._completed_at = data['completed_at']
            
        return request
        
    def __str__(self):
        """String representation of consultation request."""
        return f"Request(id={self._request_id}, student={self._student_id}, faculty={self._faculty_id}, status={self._status})" 