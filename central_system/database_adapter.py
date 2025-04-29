#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Database Adapter

This module provides a database adapter interface that allows switching
between different database backends (Firebase, PostgreSQL) without changing
application code.
"""

import os
import sys
import json
import importlib
from datetime import datetime
from abc import ABC, abstractmethod
from PyQt6.QtCore import QObject, pyqtSignal
from utils.logger import get_logger

class DatabaseAdapter(QObject, ABC):
    """
    Abstract database adapter interface.
    All concrete database implementations should inherit from this class.
    
    Signals:
        connection_changed (bool): Emitted when the connection status changes
        data_changed (str, str): Emitted when data changes (collection, document_id)
    """
    connection_changed = pyqtSignal(bool)
    data_changed = pyqtSignal(str, str)
    
    def __init__(self):
        """Initialize the database adapter."""
        super().__init__()
        self.logger = get_logger(__name__)
        self.connected = False
    
    @abstractmethod
    def connect(self):
        """Connect to the database."""
        pass
        
    @abstractmethod
    def disconnect(self):
        """Disconnect from the database."""
        pass
    
    @abstractmethod
    def get_faculty_by_id(self, faculty_id):
        """
        Get a faculty member by ID.
        
        Args:
            faculty_id (str): Faculty ID
            
        Returns:
            dict: Faculty data, or None if not found
        """
        pass
    
    @abstractmethod
    def get_student_by_id(self, student_id):
        """
        Get a student by ID.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            dict: Student data, or None if not found
        """
        pass
    
    @abstractmethod
    def get_student_by_rfid(self, rfid_id):
        """
        Get a student by RFID card ID.
        
        Args:
            rfid_id (str): RFID card ID
            
        Returns:
            dict: Student data, or None if not found
        """
        pass
    
    @abstractmethod
    def get_faculty_list(self):
        """
        Get a list of all faculty members.
        
        Returns:
            list: List of faculty members
        """
        pass
    
    @abstractmethod
    def get_office_list(self):
        """
        Get a list of all offices.
        
        Returns:
            list: List of offices
        """
        pass
    
    @abstractmethod
    def add_faculty(self, faculty_data):
        """
        Add a new faculty member.
        
        Args:
            faculty_data (dict): Faculty data
            
        Returns:
            str: Faculty ID if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def update_faculty(self, faculty_id, faculty_data):
        """
        Update faculty data.
        
        Args:
            faculty_id (str): Faculty ID
            faculty_data (dict): Faculty data
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_faculty(self, faculty_id):
        """
        Delete a faculty member.
        
        Args:
            faculty_id (str): Faculty ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def add_consultation_request(self, request_data):
        """
        Add a new consultation request.
        
        Args:
            request_data (dict): Request data
            
        Returns:
            str: Request ID if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def update_consultation_request(self, request_id, request_data):
        """
        Update consultation request data.
        
        Args:
            request_id (str): Request ID
            request_data (dict): Request data
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_requests_for_faculty(self, faculty_id, status=None):
        """
        Get consultation requests for a faculty member.
        
        Args:
            faculty_id (str): Faculty ID
            status (str, optional): Request status filter
            
        Returns:
            list: List of consultation requests
        """
        pass
    
    @abstractmethod
    def verify_admin_login(self, username, password):
        """
        Verify admin login credentials.
        
        Args:
            username (str): Admin username
            password (str): Admin password
            
        Returns:
            dict: Admin user data if credentials are valid, None otherwise
        """
        pass


class DatabaseAdapterFactory:
    """Factory for creating database adapter instances based on configuration."""
    
    @staticmethod
    def create_adapter():
        """
        Create and return a database adapter instance based on configuration.
        
        Returns:
            DatabaseAdapter: Concrete database adapter instance
        """
        logger = get_logger(__name__)
        db_type = os.getenv("DATABASE_TYPE", "firebase").lower()
        
        if db_type == "firebase":
            try:
                from data.firebase_adapter import FirebaseAdapter
                logger.info("Using Firebase database adapter")
                return FirebaseAdapter()
            except ImportError:
                logger.error("FirebaseAdapter not available, falling back to simulation mode")
                from data.simulation_adapter import SimulationAdapter
                return SimulationAdapter()
        
        elif db_type == "postgresql":
            try:
                from data.postgresql_adapter import PostgreSQLAdapter
                logger.info("Using PostgreSQL database adapter")
                return PostgreSQLAdapter()
            except ImportError:
                logger.error("PostgreSQLAdapter not available, falling back to simulation mode")
                from data.simulation_adapter import SimulationAdapter
                return SimulationAdapter()
        
        elif db_type == "simulation":
            from data.simulation_adapter import SimulationAdapter
            logger.info("Using simulation database adapter")
            return SimulationAdapter()
        
        else:
            logger.warning(f"Unsupported database type: {db_type}, falling back to simulation mode")
            from data.simulation_adapter import SimulationAdapter
            return SimulationAdapter() 