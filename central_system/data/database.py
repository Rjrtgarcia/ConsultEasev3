#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Database Manager

This module provides database functionality for the ConsultEase application.
It handles connections to Firebase and provides methods for CRUD operations.
"""

import os
import json
from datetime import datetime
import threading
import hashlib
import pytz
from PyQt6.QtCore import QObject, pyqtSignal
from utils.logger import get_logger
import time

# Try to import Firebase modules, but don't fail if not available
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class DatabaseManager(QObject):
    """
    Database manager for Firebase Firestore.
    
    Signals:
        connection_changed (bool): Emitted when the connection status changes
        data_changed (str, str): Emitted when data changes (collection, document_id)
    """
    connection_changed = pyqtSignal(bool)
    data_changed = pyqtSignal(str, str)
    
    def __init__(self, use_emulator=False):
        """
        Initialize the database manager.
        
        Args:
            use_emulator (bool, optional): Whether to use the Firebase emulator
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.db = None
        self.app = None
        self.connected = False
        self.use_emulator = use_emulator
        self.listeners = {}
        self.offline_queue = []
        self.last_connection_check = datetime.now()
        self.connection_check_interval = 60  # seconds
        self.monitoring_thread = None
        self.monitoring_running = False
        
        # Initialize Firebase
        self._initialize_firebase()
        
    def _initialize_firebase(self):
        """
        Initialize the Firebase connection.
        """
        if not FIREBASE_AVAILABLE:
            self.logger.warning("Firebase modules not available, using simulation mode")
            self._initialize_simulation()
            return
            
        try:
            # Look for service account key file
            key_file = os.path.join(os.path.dirname(__file__), 'firebase_key.json')
            if not os.path.exists(key_file):
                self.logger.warning(f"Firebase key file not found at {key_file}")
                key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'firebase_key.json')
                
            if not os.path.exists(key_file):
                self.logger.warning("Firebase key file not found, using simulation mode")
                self._initialize_simulation()
                return
                
            # Initialize Firebase with service account key
            cred = credentials.Certificate(key_file)
            self.app = firebase_admin.initialize_app(cred)
            
            # Initialize Firestore with persistence enabled for offline support
            firebase_settings = {
                'persistence': True  # Enable offline persistence
            }
            
            self.db = firestore.client(self.app, settings=firebase_settings)
            
            # Use emulator if specified
            if self.use_emulator:
                self.db.collection('_').document('_')  # Force initialization
                host = os.environ.get('FIRESTORE_EMULATOR_HOST', 'localhost:8080')
                self.logger.info(f"Using Firestore emulator at {host}")
                
            self.connected = True
            self.connection_changed.emit(True)
            self.logger.info("Firebase initialized successfully with offline persistence enabled")
            
            # Start connection monitoring thread
            self._start_connection_monitoring()
            
            # Process any pending offline operations
            self._process_offline_queue()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {e}")
            self._initialize_simulation()
            
    def _start_connection_monitoring(self):
        """
        Start a thread to monitor the Firebase connection status.
        """
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.logger.warning("Connection monitoring thread already running.")
            return
            
        self.monitoring_running = True
        
        def monitor_connection():
            while self.monitoring_running:
                try:
                    # Check connection at regular intervals
                    # Use sleep interval that allows checking self.monitoring_running more often
                    sleep_interval = 5 # Check every 5 seconds
                    for _ in range(self.connection_check_interval // sleep_interval):
                        if not self.monitoring_running:
                            break
                        time.sleep(sleep_interval)
                    
                    if not self.monitoring_running:
                        break
                    
                    # Try a simple read operation to check connection
                    if self.db and self.connected is not None:
                        try:
                            # Try to read a document
                            self.db.collection('_connection_test').document('_test').get()
                            
                            # If we get here, we're connected
                            if not self.connected:
                                self.logger.info("Firebase connection restored")
                                self.connected = True
                                self.connection_changed.emit(True)
                                
                                # Process offline queue
                                self._process_offline_queue()
                                
                        except Exception as e:
                            if self.connected:
                                self.logger.warning(f"Firebase connection lost: {e}")
                                self.connected = False
                                self.connection_changed.emit(False)
                                
                except Exception as e:
                    self.logger.error(f"Error in connection monitoring: {e}")
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=monitor_connection, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Connection monitoring thread started.")
        
    def stop_monitoring(self):
        """Stop the connection monitoring thread."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.logger.info("Stopping connection monitoring thread...")
            self.monitoring_running = False
            self.monitoring_thread.join(timeout=self.connection_check_interval + 5) # Wait a bit longer than interval
            if self.monitoring_thread.is_alive():
                self.logger.warning("Connection monitoring thread did not exit cleanly.")
            else:
                self.logger.info("Connection monitoring thread stopped.")
        self.monitoring_thread = None

    def cleanup(self):
        """Clean up database resources."""
        self.stop_monitoring()
        # Other cleanup if needed (e.g., close listeners)
        self.logger.info("DatabaseManager cleanup complete.")

    def _process_offline_queue(self):
        """
        Process operations queued during offline mode.
        """
        if not self.offline_queue:
            return
            
        self.logger.info(f"Processing {len(self.offline_queue)} queued operations")
        
        # Process each queued operation
        for operation in self.offline_queue[:]:
            try:
                op_type = operation.get('type')
                collection = operation.get('collection')
                doc_id = operation.get('doc_id')
                data = operation.get('data')
                
                if op_type == 'add':
                    # Add document
                    if doc_id:
                        self.db.collection(collection).document(doc_id).set(data)
                    else:
                        self.db.collection(collection).add(data)
                        
                elif op_type == 'update':
                    # Update document
                    self.db.collection(collection).document(doc_id).update(data)
                    
                elif op_type == 'delete':
                    # Delete document
                    self.db.collection(collection).document(doc_id).delete()
                    
                # Remove from queue if successful
                self.offline_queue.remove(operation)
                self.logger.info(f"Processed queued {op_type} operation for {collection}/{doc_id}")
                
            except Exception as e:
                self.logger.error(f"Error processing queued operation: {e}")
                
        self.logger.info(f"{len(self.offline_queue)} operations remaining in queue")
        
    def _initialize_simulation(self):
        """
        Initialize simulation mode with local data storage.
        """
        self.logger.info("Initializing database simulation mode")
        self.connected = False
        self.connection_changed.emit(False)
        
        # Create a simple in-memory database
        self.simulation_db = {
            'faculty': {},
            'students': {},
            'consultation_requests': {},
            'admin_users': {},
            'audit_log': {}
        }
        
        # Add some sample data
        self._add_sample_data()
        
    def _add_sample_data(self):
        """
        Add sample data for simulation mode.
        """
        # Sample faculty
        faculty_data = [
            {
                'id': 'faculty001',
                'name': 'Dr. John Smith',
                'department': 'Computer Science',
                'email': 'john.smith@example.com',
                'phone': '123-456-7890',
                'office': 'Room 301',
                'ble_beacon_id': 'AA:BB:CC:DD:EE:01',
                'status': 'available',
                'last_updated': datetime.now().isoformat()
            },
            {
                'id': 'faculty002',
                'name': 'Dr. Jane Johnson',
                'department': 'Electrical Engineering',
                'email': 'jane.johnson@example.com',
                'phone': '123-456-7891',
                'office': 'Room 215',
                'ble_beacon_id': 'AA:BB:CC:DD:EE:02',
                'status': 'unavailable',
                'last_updated': datetime.now().isoformat()
            },
            {
                'id': 'faculty003',
                'name': 'Dr. Robert Williams',
                'department': 'Mechanical Engineering',
                'email': 'robert.williams@example.com',
                'phone': '123-456-7892',
                'office': 'Room 118',
                'ble_beacon_id': 'AA:BB:CC:DD:EE:03',
                'status': 'available',
                'last_updated': datetime.now().isoformat()
            }
        ]
        
        # Sample students
        student_data = [
            {
                'id': 'student001',
                'name': 'Alice Brown',
                'rfid_id': 'A1B2C3D4',
                'email': 'alice.brown@example.com',
                'department': 'Computer Science',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 'student002',
                'name': 'Bob Davis',
                'rfid_id': 'E5F6G7H8',
                'email': 'bob.davis@example.com',
                'department': 'Electrical Engineering',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 'student003',
                'name': 'Charlie Evans',
                'rfid_id': 'I9J0K1L2',
                'email': 'charlie.evans@example.com',
                'department': 'Mechanical Engineering',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        # Sample consultation requests
        request_data = [
            {
                'id': 'request001',
                'student_id': 'student001',
                'faculty_id': 'faculty001',
                'request_text': 'Need help with final project',
                'course_code': 'CS101',
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            },
            {
                'id': 'request002',
                'student_id': 'student002',
                'faculty_id': 'faculty002',
                'request_text': 'Question about midterm exam',
                'course_code': 'EE201',
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        ]
        
        # Sample admin users
        admin_data = [
            {
                'id': 'admin001',
                'username': 'admin',
                'password_hash': self._hash_password('admin123'),  # Don't use in production!
                'name': 'Admin User',
                'email': 'admin@example.com',
                'role': 'administrator',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        # Add data to in-memory database
        for faculty in faculty_data:
            self.simulation_db['faculty'][faculty['id']] = faculty
            
        for student in student_data:
            self.simulation_db['students'][student['id']] = student
            
        for request in request_data:
            self.simulation_db['consultation_requests'][request['id']] = request
            
        for admin in admin_data:
            self.simulation_db['admin_users'][admin['id']] = admin
            
    def _hash_password(self, password):
        """
        Hash a password using SHA-256.
        
        Args:
            password (str): Password to hash
            
        Returns:
            str: Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
        
    def get_student_by_rfid(self, rfid_id):
        """
        Get a student by RFID ID.
        
        Args:
            rfid_id (str): RFID card ID
            
        Returns:
            dict: Student data, or None if not found
        """
        self.logger.info(f"Getting student by RFID ID: {rfid_id}")
        
        try:
            if self.db and self.connected:
                # Use Firestore
                students_ref = self.db.collection('students')
                query = students_ref.where('rfid_id', '==', rfid_id).limit(1)
                results = query.get()
                
                for doc in results:
                    student_data = doc.to_dict()
                    student_data['id'] = doc.id
                    return student_data
                    
                return None
            else:
                # Use simulation DB
                for student_id, student in self.simulation_db['students'].items():
                    if student.get('rfid_id') == rfid_id:
                        return student
                        
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting student by RFID: {e}")
            return None
            
    def get_student_by_id(self, student_id):
        """
        Get a student by ID.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            dict: Student data, or None if not found
        """
        self.logger.info(f"Getting student by ID: {student_id}")
        
        try:
            if self.db and self.connected:
                # Use Firestore
                doc_ref = self.db.collection('students').document(student_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    student_data = doc.to_dict()
                    student_data['id'] = doc.id
                    return student_data
                    
                return None
            else:
                # Use simulation DB
                return self.simulation_db['students'].get(student_id)
                
        except Exception as e:
            self.logger.error(f"Error getting student by ID: {e}")
            return None
    
    def get_student_by_email(self, email):
        """
        Get a student by email.
        
        Args:
            email (str): Student email
            
        Returns:
            dict: Student data, or None if not found
        """
        self.logger.info(f"Getting student by email: {email}")
        
        try:
            if self.db and self.connected:
                # Use Firestore
                students_ref = self.db.collection('students')
                query = students_ref.where('email', '==', email).limit(1)
                results = query.get()
                
                for doc in results:
                    student_data = doc.to_dict()
                    student_data['id'] = doc.id
                    return student_data
                    
                return None
            else:
                # Use simulation DB
                for student_id, student in self.simulation_db['students'].items():
                    if student.get('email') == email:
                        return student
                        
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting student by email: {e}")
            return None
            
    def update_student(self, student_id, student_data):
        """
        Update student data.
        
        Args:
            student_id (str): Student ID
            student_data (dict): Student data
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Updating student: {student_id}")
        
        try:
            if self.db and self.connected:
                # Use Firestore
                doc_ref = self.db.collection('students').document(student_id)
                doc_ref.update(student_data)
            else:
                # Use simulation DB
                if student_id in self.simulation_db['students']:
                    self.simulation_db['students'][student_id].update(student_data)
                else:
                    self.simulation_db['students'][student_id] = student_data
                    
            # Emit data changed signal
            self.data_changed.emit('students', student_id)
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating student: {e}")
            return False
            
    def get_all_faculty(self, department=None, status=None):
        """
        Get all faculty members, optionally filtered by department and/or status.
        
        Args:
            department (str, optional): Filter by department
            status (str, optional): Filter by status
            
        Returns:
            list: List of faculty data
        """
        self.logger.info("Getting all faculty")
        
        try:
            faculty_list = []
            
            if self.db and self.connected:
                # Use Firestore
                faculty_ref = self.db.collection('faculty')
                
                # Apply filters
                if department:
                    faculty_ref = faculty_ref.where('department', '==', department)
                if status:
                    faculty_ref = faculty_ref.where('status', '==', status)
                    
                results = faculty_ref.get()
                
                for doc in results:
                    faculty_data = doc.to_dict()
                    faculty_data['id'] = doc.id
                    faculty_list.append(faculty_data)
            else:
                # Use simulation DB
                for faculty_id, faculty in self.simulation_db['faculty'].items():
                    if department and faculty.get('department') != department:
                        continue
                    if status and faculty.get('status') != status:
                        continue
                        
                    faculty_list.append(faculty.copy())
                    
            return faculty_list
            
        except Exception as e:
            self.logger.error(f"Error getting faculty: {e}")
            return []
            
    def add_faculty(self, faculty_data):
        """
        Add a new faculty member.
        
        Args:
            faculty_data (dict): Faculty data
            
        Returns:
            str: Faculty ID if successful, None otherwise
        """
        self.logger.info("Adding new faculty")
        
        try:
            # Make sure required fields are present
            required_fields = ['name', 'department', 'email']
            for field in required_fields:
                if field not in faculty_data:
                    self.logger.error(f"Missing required field: {field}")
                    return None
                    
            # Set defaults if not provided
            faculty_data.setdefault('status', 'unavailable')
            faculty_data.setdefault('last_updated', datetime.now().isoformat())
        
            if self.db and self.connected:
                # Use Firestore
                doc_ref = self.db.collection('faculty').document()
                doc_ref.set(faculty_data)
                faculty_id = doc_ref.id
            else:
                # Use simulation DB
                faculty_id = faculty_data.get('id') or f"faculty{len(self.simulation_db['faculty']) + 1:03d}"
            faculty_data['id'] = faculty_id
            self.simulation_db['faculty'][faculty_id] = faculty_data
            
            # Emit data changed signal
            self.data_changed.emit('faculty', faculty_id)
            return faculty_id
            
        except Exception as e:
            self.logger.error(f"Error adding faculty: {e}")
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
        
        try:
            # Update last updated timestamp
            faculty_data['last_updated'] = datetime.now().isoformat()
            
            if self.db and self.connected:
                # Use Firestore
                doc_ref = self.db.collection('faculty').document(faculty_id)
                doc_ref.update(faculty_data)
            else:
                # Use simulation DB
                if faculty_id in self.simulation_db['faculty']:
                    self.simulation_db['faculty'][faculty_id].update(faculty_data)
                else:
                    faculty_data['id'] = faculty_id
                    self.simulation_db['faculty'][faculty_id] = faculty_data
            
            # Emit data changed signal
            self.data_changed.emit('faculty', faculty_id)
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating faculty: {e}")
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
        
        try:
            if self.db and self.connected:
                # Use Firestore
                doc_ref = self.db.collection('faculty').document(faculty_id)
                doc_ref.delete()
            else:
                # Use simulation DB
                if faculty_id in self.simulation_db['faculty']:
                    del self.simulation_db['faculty'][faculty_id]
            
            # Emit data changed signal
            self.data_changed.emit('faculty', faculty_id)
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting faculty: {e}")
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
        
        try:
            # Make sure required fields are present
            required_fields = ['student_id', 'faculty_id', 'request_text']
            for field in required_fields:
                if field not in request_data:
                    self.logger.error(f"Missing required field: {field}")
                    return None
        
            # Set defaults if not provided
            request_data.setdefault('status', 'pending')
            now = datetime.now().isoformat()
            request_data.setdefault('created_at', now)
            request_data.setdefault('updated_at', now)
        
            if self.db and self.connected:
                # Use Firestore
                doc_ref = self.db.collection('consultation_requests').document()
                doc_ref.set(request_data)
                request_id = doc_ref.id
            else:
                # Use simulation DB
                request_id = request_data.get('id') or f"request{len(self.simulation_db['consultation_requests']) + 1:03d}"
            request_data['id'] = request_id
            self.simulation_db['consultation_requests'][request_id] = request_data
            
            # Emit data changed signal
            self.data_changed.emit('consultation_requests', request_id)
            return request_id
            
        except Exception as e:
            self.logger.error(f"Error adding consultation request: {e}")
            return None
            
    def get_faculty_requests(self, faculty_id):
        """
        Get consultation requests for a faculty member.
        
        Args:
            faculty_id (str): Faculty ID
            
        Returns:
            list: List of request data
        """
        self.logger.info(f"Getting consultation requests for faculty: {faculty_id}")
        
        try:
            request_list = []
            
            if self.db and self.connected:
                # Use Firestore
                requests_ref = self.db.collection('consultation_requests')
                query = requests_ref.where('faculty_id', '==', faculty_id)
                results = query.get()
                
                for doc in results:
                    request_data = doc.to_dict()
                    request_data['id'] = doc.id
                    request_list.append(request_data)
            else:
                # Use simulation DB
                for request_id, request in self.simulation_db['consultation_requests'].items():
                    if request.get('faculty_id') == faculty_id:
                        request_list.append(request.copy())
                        
            return request_list
            
        except Exception as e:
            self.logger.error(f"Error getting faculty requests: {e}")
            return []
            
    def get_student_requests(self, student_id):
        """
        Get consultation requests for a student.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            list: List of request data
        """
        self.logger.info(f"Getting consultation requests for student: {student_id}")
        
        try:
            request_list = []
            
            if self.db and self.connected:
                # Use Firestore
                requests_ref = self.db.collection('consultation_requests')
                query = requests_ref.where('student_id', '==', student_id)
                results = query.get()
                
                for doc in results:
                    request_data = doc.to_dict()
                    request_data['id'] = doc.id
                    request_list.append(request_data)
            else:
                # Use simulation DB
                for request_id, request in self.simulation_db['consultation_requests'].items():
                    if request.get('student_id') == student_id:
                        request_list.append(request.copy())
                        
            return request_list
            
        except Exception as e:
            self.logger.error(f"Error getting student requests: {e}")
            return []
            
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
        
        try:
            # Update last updated timestamp
            request_data['updated_at'] = datetime.now().isoformat()
            
            if self.db and self.connected:
                # Use Firestore
                doc_ref = self.db.collection('consultation_requests').document(request_id)
                doc_ref.update(request_data)
            else:
                # Use simulation DB
                if request_id in self.simulation_db['consultation_requests']:
                    self.simulation_db['consultation_requests'][request_id].update(request_data)
                else:
                    request_data['id'] = request_id
                    self.simulation_db['consultation_requests'][request_id] = request_data
                    
            # Emit data changed signal
            self.data_changed.emit('consultation_requests', request_id)
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating consultation request: {e}")
            return False
            
    def add_audit_log(self, log_data):
        """
        Add a new audit log entry.
        
        Args:
            log_data (dict): Log data
            
        Returns:
            str: Log ID if successful, None otherwise
        """
        self.logger.info("Adding audit log entry")
        
        try:
            # Set defaults if not provided
            log_data.setdefault('timestamp', datetime.now().isoformat())
            
            if self.db and self.connected:
                # Use Firestore
                doc_ref = self.db.collection('audit_log').document()
                doc_ref.set(log_data)
                log_id = doc_ref.id
            else:
                # Use simulation DB
                log_id = f"log{len(self.simulation_db['audit_log']) + 1:05d}"
            log_data['id'] = log_id
            self.simulation_db['audit_log'][log_id] = log_data
                
            return log_id
            
        except Exception as e:
            self.logger.error(f"Error adding audit log: {e}")
            return None
            
    def get_audit_logs(self, limit=50):
        """
        Get audit log entries.
        
        Args:
            limit (int, optional): Maximum number of entries to return
            
        Returns:
            list: List of log entries
        """
        self.logger.info(f"Getting audit logs (limit: {limit})")
        
        try:
            log_list = []
            
            if self.db and self.connected:
                # Use Firestore
                logs_ref = self.db.collection('audit_log')
                query = logs_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
                results = query.get()
                
                for doc in results:
                    log_data = doc.to_dict()
                    log_data['id'] = doc.id
                    log_list.append(log_data)
            else:
                # Use simulation DB
                logs = list(self.simulation_db['audit_log'].values())
                logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                log_list = logs[:limit]
                
            return log_list
            
        except Exception as e:
            self.logger.error(f"Error getting audit logs: {e}")
            return []
            
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
        
        try:
            password_hash = self._hash_password(password)
            
            if self.db and self.connected:
                # Use Firestore
                admin_ref = self.db.collection('admin_users')
                query = admin_ref.where('username', '==', username).limit(1)
                results = query.get()
                
                for doc in results:
                    admin_data = doc.to_dict()
                    if admin_data.get('password_hash') == password_hash:
                        admin_data['id'] = doc.id
                        return admin_data
                        
                    return None
            else:
                # Use simulation DB
                for admin_id, admin in self.simulation_db['admin_users'].items():
                    if admin.get('username') == username and admin.get('password_hash') == password_hash:
                        return admin.copy()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error verifying admin login: {e}")
            return None

    def add_offline_operation(self, operation_type, collection, doc_id=None, data=None):
        """
        Add an operation to the offline queue.
        
        Args:
            operation_type (str): Type of operation ('add', 'update', 'delete')
            collection (str): Collection name
            doc_id (str, optional): Document ID
            data (dict, optional): Document data
            
        Returns:
            bool: True if added to queue, False on error
        """
        try:
            operation = {
                'type': operation_type,
                'collection': collection,
                'doc_id': doc_id,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            self.offline_queue.append(operation)
            self.logger.info(f"Added {operation_type} operation to offline queue for {collection}/{doc_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding operation to offline queue: {e}")
            return False
