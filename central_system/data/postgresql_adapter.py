#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - PostgreSQL Database Adapter

This module provides a PostgreSQL database adapter implementation
for the ConsultEase application. It allows replacing Firebase with
PostgreSQL for university environments.
"""

import os
import json
import hashlib
import threading
import time
from datetime import datetime
import uuid

from PyQt6.QtCore import QObject, pyqtSignal
from utils.logger import get_logger

# Import PostgreSQL library
try:
    import psycopg2
    import psycopg2.extras
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

# Import base adapter class
from central_system.database_adapter import DatabaseAdapter

class PostgreSQLAdapter(DatabaseAdapter):
    """
    PostgreSQL database adapter implementation.
    
    Provides implementation of database operations using PostgreSQL.
    """
    
    def __init__(self):
        """Initialize the PostgreSQL adapter."""
        super().__init__()
        self.logger = get_logger(__name__)
        self.db_params = {
            'dbname': os.getenv('POSTGRESQL_DBNAME', 'consultease'),
            'user': os.getenv('POSTGRESQL_USER', 'postgres'),
            'password': os.getenv('POSTGRESQL_PASSWORD', ''),
            'host': os.getenv('POSTGRESQL_HOST', 'localhost'),
            'port': os.getenv('POSTGRESQL_PORT', '5432')
        }
        self.conn = None
        self.connected = False
        
        # Initialize connection
        self.connect()
        
    def connect(self):
        """Connect to the PostgreSQL database."""
        if not POSTGRESQL_AVAILABLE:
            self.logger.error("PostgreSQL module not available")
            self.connected = False
            self.connection_changed.emit(False)
            return False
            
        try:
            self.logger.info(f"Connecting to PostgreSQL database at {self.db_params['host']}:{self.db_params['port']}")
            self.conn = psycopg2.connect(**self.db_params)
            self.conn.autocommit = True
            
            # Initialize tables
            self._initialize_tables()
            
            self.connected = True
            self.connection_changed.emit(True)
            self.logger.info("Connected to PostgreSQL database")
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to PostgreSQL database: {e}")
            self.connected = False
            self.connection_changed.emit(False)
            return False
            
    def disconnect(self):
        """Disconnect from the PostgreSQL database."""
        if self.conn:
            try:
                self.conn.close()
                self.logger.info("Disconnected from PostgreSQL database")
            except Exception as e:
                self.logger.error(f"Error disconnecting from PostgreSQL database: {e}")
            finally:
                self.conn = None
                self.connected = False
                self.connection_changed.emit(False)
                
    def _initialize_tables(self):
        """Initialize database tables if they don't exist."""
        if not self.conn:
            return
            
        try:
            with self.conn.cursor() as cur:
                # Faculty table
                cur.execute("""
                CREATE TABLE IF NOT EXISTS faculty (
                    faculty_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    office VARCHAR(50),
                    ble_beacon_id VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'unavailable',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Students table
                cur.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    rfid_id VARCHAR(50) UNIQUE,
                    last_login TIMESTAMP
                )
                """)
                
                # Offices table
                cur.execute("""
                CREATE TABLE IF NOT EXISTS offices (
                    office_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    building VARCHAR(100) NOT NULL,
                    floor INTEGER DEFAULT 1,
                    room VARCHAR(20) NOT NULL,
                    ble_beacon_id VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'active',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Consultation requests table
                cur.execute("""
                CREATE TABLE IF NOT EXISTS consultation_requests (
                    request_id VARCHAR(50) PRIMARY KEY,
                    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id),
                    faculty_id VARCHAR(50) NOT NULL REFERENCES faculty(faculty_id),
                    subject VARCHAR(200) NOT NULL,
                    message TEXT,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Consultations table
                cur.execute("""
                CREATE TABLE IF NOT EXISTS consultations (
                    consultation_id VARCHAR(50) PRIMARY KEY,
                    request_id VARCHAR(50) REFERENCES consultation_requests(request_id),
                    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id),
                    faculty_id VARCHAR(50) NOT NULL REFERENCES faculty(faculty_id),
                    subject VARCHAR(200) NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    notes TEXT,
                    status VARCHAR(20) DEFAULT 'scheduled',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Admin users table
                cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    admin_id VARCHAR(50) PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(128) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    role VARCHAR(20) DEFAULT 'admin',
                    last_login TIMESTAMP
                )
                """)
                
                # Audit log table
                cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    log_id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50),
                    action VARCHAR(50) NOT NULL,
                    entity_type VARCHAR(50) NOT NULL,
                    entity_id VARCHAR(50),
                    details JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Check if default admin exists, create if not
                cur.execute("SELECT COUNT(*) FROM admin_users WHERE username = 'admin'")
                if cur.fetchone()[0] == 0:
                    # Create default admin
                    admin_id = str(uuid.uuid4())
                    password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                    cur.execute("""
                    INSERT INTO admin_users (admin_id, username, password_hash, name, email, role)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """, (admin_id, "admin", password_hash, "Administrator", "admin@consultease.edu", "superadmin"))
                    self.logger.info("Created default admin user (username: admin, password: admin123)")
                
                self.logger.info("Database tables initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing database tables: {e}")
            raise
            
    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """
        Execute a database query.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters
            fetch_one (bool, optional): Whether to fetch one result
            fetch_all (bool, optional): Whether to fetch all results
            
        Returns:
            mixed: Query results if fetch_one or fetch_all is True, else None
        """
        if not self.conn:
            try:
                self.connect()
            except Exception as e:
                self.logger.error(f"Failed to reconnect to database: {e}")
                return None
                
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, params or ())
                
                if fetch_one:
                    result = cur.fetchone()
                    return dict(result) if result else None
                elif fetch_all:
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                    
                return True
                
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            return None
            
    def _generate_id(self, prefix=""):
        """
        Generate a unique ID for database records.
        
        Args:
            prefix (str, optional): ID prefix
            
        Returns:
            str: Unique ID
        """
        return f"{prefix}{str(uuid.uuid4())}"
    
    def get_faculty_by_id(self, faculty_id):
        """
        Get a faculty member by ID.
        
        Args:
            faculty_id (str): Faculty ID
            
        Returns:
            dict: Faculty data, or None if not found
        """
        self.logger.info(f"Getting faculty by ID: {faculty_id}")
        
        query = "SELECT * FROM faculty WHERE faculty_id = %s"
        return self._execute_query(query, (faculty_id,), fetch_one=True)
    
    def get_student_by_id(self, student_id):
        """
        Get a student by ID.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            dict: Student data, or None if not found
        """
        self.logger.info(f"Getting student by ID: {student_id}")
        
        query = "SELECT * FROM students WHERE student_id = %s"
        return self._execute_query(query, (student_id,), fetch_one=True)
    
    def get_student_by_rfid(self, rfid_id):
        """
        Get a student by RFID card ID.
        
        Args:
            rfid_id (str): RFID card ID
            
        Returns:
            dict: Student data, or None if not found
        """
        self.logger.info(f"Getting student by RFID: {rfid_id}")
        
        query = "SELECT * FROM students WHERE rfid_id = %s"
        student = self._execute_query(query, (rfid_id,), fetch_one=True)
        
        if student:
            # Update last login time
            update_query = "UPDATE students SET last_login = CURRENT_TIMESTAMP WHERE student_id = %s"
            self._execute_query(update_query, (student['student_id'],))
            
        return student
    
    def get_faculty_list(self):
        """
        Get a list of all faculty members.
        
        Returns:
            list: List of faculty members
        """
        self.logger.info("Getting faculty list")
        
        query = "SELECT * FROM faculty ORDER BY name"
        return self._execute_query(query, fetch_all=True)
    
    def get_office_list(self):
        """
        Get a list of all offices.
        
        Returns:
            list: List of offices
        """
        self.logger.info("Getting office list")
        
        query = "SELECT * FROM offices ORDER BY building, floor, room"
        return self._execute_query(query, fetch_all=True)
    
    def add_faculty(self, faculty_data):
        """
        Add a new faculty member.
        
        Args:
            faculty_data (dict): Faculty data
            
        Returns:
            str: Faculty ID if successful, None otherwise
        """
        self.logger.info("Adding new faculty")
        
        # Make sure required fields are present
        required_fields = ['name', 'department', 'email']
        for field in required_fields:
            if field not in faculty_data:
                self.logger.error(f"Missing required field: {field}")
                return None
                
        # Generate ID if not provided
        faculty_id = faculty_data.get('faculty_id') or self._generate_id("faculty_")
        
        # Insert into database
        query = """
        INSERT INTO faculty (
            faculty_id, name, department, email, phone, office, 
            ble_beacon_id, status, last_updated
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        RETURNING faculty_id
        """
        
        params = (
            faculty_id,
            faculty_data.get('name'),
            faculty_data.get('department'),
            faculty_data.get('email'),
            faculty_data.get('phone'),
            faculty_data.get('office'),
            faculty_data.get('ble_beacon_id'),
            faculty_data.get('status', 'unavailable')
        )
        
        result = self._execute_query(query, params, fetch_one=True)
        
        if result:
            # Emit data changed signal
            self.data_changed.emit('faculty', faculty_id)
            return faculty_id
            
        return None
    
    def update_faculty(self, faculty_id, faculty_data):
        """
        Update faculty data.
        
        Args:
            faculty_id (str): Faculty ID
            faculty_data (dict): Faculty data
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Updating faculty: {faculty_id}")
        
        # Build update query dynamically based on provided fields
        fields = []
        params = []
        
        for key, value in faculty_data.items():
            if key != 'faculty_id':  # Skip ID field
                fields.append(f"{key} = %s")
                params.append(value)
                
        # Add timestamp and ID
        fields.append("last_updated = CURRENT_TIMESTAMP")
        params.append(faculty_id)
        
        query = f"UPDATE faculty SET {', '.join(fields)} WHERE faculty_id = %s"
        
        result = self._execute_query(query, tuple(params))
        
        if result:
            # Emit data changed signal
            self.data_changed.emit('faculty', faculty_id)
            return True
            
        return False
    
    def delete_faculty(self, faculty_id):
        """
        Delete a faculty member.
        
        Args:
            faculty_id (str): Faculty ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Deleting faculty: {faculty_id}")
        
        # Check for dependencies (consultations, requests)
        check_query = """
        SELECT COUNT(*) FROM consultation_requests WHERE faculty_id = %s
        UNION ALL
        SELECT COUNT(*) FROM consultations WHERE faculty_id = %s
        """
        
        result = self._execute_query(check_query, (faculty_id, faculty_id), fetch_all=True)
        
        if result and (result[0]['count'] > 0 or result[1]['count'] > 0):
            self.logger.warning(f"Faculty {faculty_id} has associated consultations, cannot delete")
            return False
            
        # Delete faculty
        query = "DELETE FROM faculty WHERE faculty_id = %s"
        result = self._execute_query(query, (faculty_id,))
        
        if result:
            # Emit data changed signal
            self.data_changed.emit('faculty', faculty_id)
            return True
            
        return False
    
    def add_consultation_request(self, request_data):
        """
        Add a new consultation request.
        
        Args:
            request_data (dict): Request data
            
        Returns:
            str: Request ID if successful, None otherwise
        """
        self.logger.info("Adding new consultation request")
        
        # Make sure required fields are present
        required_fields = ['student_id', 'faculty_id', 'subject']
        for field in required_fields:
            if field not in request_data:
                self.logger.error(f"Missing required field: {field}")
                return None
                
        # Generate ID if not provided
        request_id = request_data.get('request_id') or self._generate_id("req_")
        
        # Insert into database
        query = """
        INSERT INTO consultation_requests (
            request_id, student_id, faculty_id, subject, message,
            status, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING request_id
        """
        
        params = (
            request_id,
            request_data.get('student_id'),
            request_data.get('faculty_id'),
            request_data.get('subject'),
            request_data.get('message'),
            request_data.get('status', 'pending')
        )
        
        result = self._execute_query(query, params, fetch_one=True)
        
        if result:
            # Emit data changed signal
            self.data_changed.emit('consultation_requests', request_id)
            return request_id
            
        return None
    
    def update_consultation_request(self, request_id, request_data):
        """
        Update consultation request data.
        
        Args:
            request_id (str): Request ID
            request_data (dict): Request data
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Updating consultation request: {request_id}")
        
        # Build update query dynamically based on provided fields
        fields = []
        params = []
        
        for key, value in request_data.items():
            if key != 'request_id':  # Skip ID field
                fields.append(f"{key} = %s")
                params.append(value)
                
        # Add timestamp and ID
        fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(request_id)
        
        query = f"UPDATE consultation_requests SET {', '.join(fields)} WHERE request_id = %s"
        
        result = self._execute_query(query, tuple(params))
        
        if result:
            # Emit data changed signal
            self.data_changed.emit('consultation_requests', request_id)
            return True
            
        return False
    
    def get_requests_for_faculty(self, faculty_id, status=None):
        """
        Get consultation requests for a faculty member.
        
        Args:
            faculty_id (str): Faculty ID
            status (str, optional): Request status filter
            
        Returns:
            list: List of consultation requests
        """
        self.logger.info(f"Getting consultation requests for faculty: {faculty_id}")
        
        if status:
            query = """
            SELECT r.*, s.name as student_name
            FROM consultation_requests r
            JOIN students s ON r.student_id = s.student_id
            WHERE r.faculty_id = %s AND r.status = %s
            ORDER BY r.created_at DESC
            """
            return self._execute_query(query, (faculty_id, status), fetch_all=True)
        else:
            query = """
            SELECT r.*, s.name as student_name
            FROM consultation_requests r
            JOIN students s ON r.student_id = s.student_id
            WHERE r.faculty_id = %s
            ORDER BY r.created_at DESC
            """
            return self._execute_query(query, (faculty_id,), fetch_all=True)
    
    def verify_admin_login(self, username, password):
        """
        Verify admin login credentials.
        
        Args:
            username (str): Admin username
            password (str): Admin password
            
        Returns:
            dict: Admin user data if credentials are valid, None otherwise
        """
        self.logger.info(f"Verifying admin login: {username}")
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Check credentials
        query = """
        SELECT * FROM admin_users
        WHERE username = %s AND password_hash = %s
        """
        
        admin = self._execute_query(query, (username, password_hash), fetch_one=True)
        
        if admin:
            # Update last login
            update_query = "UPDATE admin_users SET last_login = CURRENT_TIMESTAMP WHERE admin_id = %s"
            self._execute_query(update_query, (admin['admin_id'],))
            
            return admin
            
        return None 