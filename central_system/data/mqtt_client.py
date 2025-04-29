#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - MQTT Client

This module provides MQTT client functionality for the ConsultEase application.
It handles communication between the central system and faculty desk units.
"""

import os
import json
import threading
import time
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from utils.logger import get_logger

# Try to import MQTT module, but don't fail if not available
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

class MQTTClient(QObject):
    """
    MQTT client for communication with faculty desk units.
    
    Signals:
        connection_changed (bool): Emitted when the connection status changes
        message_received (str, str): Emitted when a message is received (topic, payload)
        faculty_status_changed (str, str): Emitted when faculty status changes (faculty_id, status)
        request_received (dict): Emitted when a consultation request is received
    """
    connection_changed = pyqtSignal(bool)
    message_received = pyqtSignal(str, str)
    faculty_status_changed = pyqtSignal(str, str)
    request_received = pyqtSignal(dict)
    
    def __init__(self, broker="localhost", port=1883, client_id=None, username=None, password=None):
        """
        Initialize the MQTT client.
        
        Args:
            broker (str, optional): MQTT broker address
            port (int, optional): MQTT broker port
            client_id (str, optional): Client ID for MQTT connection
            username (str, optional): Username for MQTT broker authentication
            password (str, optional): Password for MQTT broker authentication
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password
        self.client = None
        self.connected = False
        self.reconnect_timer = None
        self.reconnect_interval = 5  # seconds
        self.max_reconnect_interval = 300  # 5 minutes
        self.current_reconnect_interval = self.reconnect_interval
        self.topics = {
            'faculty_status': 'faculty/+/status',
            'faculty_requests': 'faculty/+/requests',
            'notifications': 'consultease/notifications'
        }
        
        # Message queue for when connection is lost
        self.message_queue = []
        self.max_queue_size = 100  # Limit queue size to prevent memory issues
        
        # Initialize MQTT client
        self._initialize_mqtt()
        
    def _initialize_mqtt(self):
        """
        Initialize the MQTT client.
        """
        if not MQTT_AVAILABLE:
            self.logger.warning("MQTT module not available, using simulation mode")
            self._initialize_simulation()
            return
            
        try:
            # Use a persistent client ID if none provided
            if not self.client_id:
                self.client_id = f"consultease-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create MQTT client with persistence for QoS > 0 messages
            persistence_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mqtt_persistence")
            os.makedirs(persistence_path, exist_ok=True)
            
            self.client = mqtt.Client(
                client_id=self.client_id,
                clean_session=False,  # Use persistent sessions
                protocol=mqtt.MQTTv311,
                transport="tcp"
            )
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # Set MQTT broker credentials if provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # Set will message for unexpected disconnects
            will_payload = json.dumps({
                "status": "offline",
                "timestamp": datetime.now().isoformat()
            })
            self.client.will_set(
                topic=f"consultease/system/{self.client_id}/status",
                payload=will_payload,
                qos=1,
                retain=True
            )
            
            self.logger.info("MQTT client initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MQTT client: {e}")
            self._initialize_simulation()
            
    def _initialize_simulation(self):
        """
        Initialize simulation mode for MQTT.
        """
        self.logger.info("Initializing MQTT simulation mode")
        self.client = None
        self.connected = False
        self.connection_changed.emit(False)
        
        # Create a simple in-memory message store
        self.simulation_messages = []
        
        # Start a timer to simulate receiving messages
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self._simulate_messages)
        self.simulation_timer.start(10000)  # 10 seconds
        
    def _simulate_messages(self):
        """
        Simulate receiving MQTT messages in simulation mode.
        """
        if not self.connected:
            return
            
        # Simulate faculty status updates
        faculty_ids = ['faculty001', 'faculty002', 'faculty003']
        statuses = ['available', 'unavailable']
        
        import random
        faculty_id = random.choice(faculty_ids)
        status = random.choice(statuses)
        
        topic = f"faculty/{faculty_id}/status"
        payload = json.dumps({
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
        self.logger.info(f"Simulating MQTT message: {topic} - {payload}")
        self._process_message(topic, payload)
        
    def connect(self):
        """
        Connect to the MQTT broker.
        
        Returns:
            bool: True if connection was initiated, False otherwise
        """
        if self.connected:
            self.logger.warning("Already connected to MQTT broker")
            return True
            
        if not MQTT_AVAILABLE:
            self.logger.warning("MQTT module not available, using simulation mode")
            self.connected = True
            self.connection_changed.emit(True)
            return True
            
        if not self.client:
            self.logger.error("MQTT client not initialized")
            return False
            
        try:
            self.logger.info(f"Connecting to MQTT broker at {self.broker}:{self.port}")
            
            # Set connection timeout and keep alive
            self.client.connect_async(self.broker, self.port, keepalive=60)
            
            # Start the network loop in a background thread
            self.client.loop_start()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            self._start_reconnect_timer()
            return False
            
    def disconnect(self):
        """
        Disconnect from the MQTT broker.
        """
        if not self.connected:
            self.logger.warning("Not connected to MQTT broker")
            return
            
        if not MQTT_AVAILABLE or not self.client:
            self.connected = False
            self.connection_changed.emit(False)
            
            if hasattr(self, 'simulation_timer'):
                self.simulation_timer.stop()
                
            return
            
        try:
            # Publish offline status before disconnecting
            self._publish_system_status("offline")
            
            self.logger.info("Disconnecting from MQTT broker")
            self.client.loop_stop()
            self.client.disconnect()
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from MQTT broker: {e}")
            
        finally:
            self.connected = False
            self.connection_changed.emit(False)
            
    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client connects to the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data
            flags: Connection flags
            rc: Connection result code
        """
        if rc == 0:
            self.logger.info("Connected to MQTT broker")
            self.connected = True
            self.connection_changed.emit(True)
            
            # Reset reconnect interval on successful connection
            self.current_reconnect_interval = self.reconnect_interval
            
            # Subscribe to topics
            for topic in self.topics.values():
                self.client.subscribe(topic, qos=1)
                self.logger.info(f"Subscribed to {topic}")
                
            # Publish online status
            self._publish_system_status("online")
            
            # Process any queued messages
            self._process_message_queue()
        else:
            error_message = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized"
            }.get(rc, f"Connection failed with code {rc}")
            
            self.logger.error(f"MQTT connection failed: {error_message}")
            self.connected = False
            self.connection_changed.emit(False)
            self._start_reconnect_timer()
            
    def _on_disconnect(self, client, userdata, rc):
        """
        Callback for when the client disconnects from the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data
            rc: Disconnection result code
        """
        if rc != 0:
            self.logger.warning(f"Unexpected MQTT disconnection: {rc}")
            self.connected = False
            self.connection_changed.emit(False)
            self._start_reconnect_timer()
        else:
            self.logger.info("Disconnected from MQTT broker")
            self.connected = False
            self.connection_changed.emit(False)
            
    def _on_message(self, client, userdata, msg):
        """
        Callback for when a message is received from the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data
            msg: MQTT message
        """
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
        self.logger.debug(f"Received MQTT message: {topic} - {payload}")
        self.message_received.emit(topic, payload)
            
            # Process the message
            self._process_message(topic, payload)
            
    def _process_message(self, topic, payload):
        """
        Process a received MQTT message.
        
        Args:
            topic (str): MQTT topic
            payload (str): Message payload
        """
        try:
            # Parse the JSON payload
            data = json.loads(payload)
        
        # Process faculty status updates
        if topic.startswith('faculty/') and topic.endswith('/status'):
                faculty_id = topic.split('/')[1]
                status = data.get('status')
                if status:
                    self.logger.info(f"Faculty status changed: {faculty_id} -> {status}")
                self.faculty_status_changed.emit(faculty_id, status)
                
        # Process consultation requests
        elif topic.startswith('faculty/') and topic.endswith('/requests'):
                faculty_id = topic.split('/')[1]
                    data['faculty_id'] = faculty_id
                self.logger.info(f"Consultation request received for {faculty_id}")
                self.request_received.emit(data)
                
            # Process system notifications
            elif topic.startswith('consultease/notifications'):
                self.logger.info(f"System notification received: {data.get('message', '')}")
                
        except json.JSONDecodeError:
            self.logger.warning(f"Received invalid JSON payload: {payload}")
            except Exception as e:
            self.logger.error(f"Error processing MQTT message: {e}")
                
    def _start_reconnect_timer(self):
        """
        Start the reconnect timer with exponential backoff.
        """
        # Stop any existing timer
        if self.reconnect_timer:
            self.reconnect_timer.cancel()
            
        # Start a new timer with current backoff interval
        self.reconnect_timer = threading.Timer(self.current_reconnect_interval, self._reconnect)
        self.reconnect_timer.daemon = True
        self.reconnect_timer.start()
        
        self.logger.info(f"Scheduled reconnection attempt in {self.current_reconnect_interval} seconds")
        
        # Increase backoff interval for next attempt (exponential with cap)
        self.current_reconnect_interval = min(
            self.current_reconnect_interval * 2,
            self.max_reconnect_interval
        )
    
    def _reconnect(self):
        """
        Attempt to reconnect to the MQTT broker.
        """
        if self.connected:
            return
            
        try:
            self.logger.info(f"Attempting to reconnect to MQTT broker at {self.broker}:{self.port}")
            self.client.reconnect()
        except Exception as e:
            self.logger.error(f"Reconnection attempt failed: {e}")
            self._start_reconnect_timer()
            
    def _publish_system_status(self, status):
        """
        Publish system status information.
        
        Args:
            status (str): Status to publish (online/offline)
        """
        if not self.client:
            return
            
        try:
            topic = f"consultease/system/{self.client_id}/status"
            payload = json.dumps({
                "status": status,
                "timestamp": datetime.now().isoformat()
            })
            
            self.client.publish(topic, payload, qos=1, retain=True)
            self.logger.info(f"Published system status: {status}")
        except Exception as e:
            self.logger.error(f"Error publishing system status: {e}")
    
    def _process_message_queue(self):
        """
        Process queued messages that couldn't be sent during disconnection.
        """
        if not self.message_queue:
            return
            
        self.logger.info(f"Processing {len(self.message_queue)} queued messages")
        
        # Copy the queue and clear it
        queued_messages = self.message_queue.copy()
        self.message_queue.clear()
        
        # Publish each queued message
        for msg in queued_messages:
            self.publish(msg['topic'], msg['payload'], msg['qos'], msg['retain'])
        
    def publish_faculty_status(self, faculty_id, status):
        """
        Publish faculty status update.
        
        Args:
            faculty_id (str): Faculty ID
            status (str): Faculty status (available, busy, unavailable, etc.)
            
        Returns:
            bool: True if the message was published successfully
        """
        topic = f"faculty/{faculty_id}/status"
        payload = json.dumps({
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
        return self.publish(topic, payload, qos=1, retain=True)
        
    def publish_consultation_request(self, request_data):
        """
        Publish consultation request.
        
        Args:
            request_data (dict): Consultation request data
                - faculty_id: ID of the faculty member
                - student_id: ID of the student
                - subject: Subject of the consultation
                - message: Additional message
            
        Returns:
            bool: True if the message was published successfully
        """
        faculty_id = request_data.get('faculty_id')
        if not faculty_id:
            self.logger.error("Cannot publish consultation request without faculty_id")
            return False
            
        topic = f"faculty/{faculty_id}/requests"
        payload = json.dumps({
            **request_data,
            'timestamp': datetime.now().isoformat()
        })
        
        return self.publish(topic, payload, qos=1)
        
    def publish_notification(self, notification_data):
        """
        Publish system notification.
        
        Args:
            notification_data (dict): Notification data
                - message: Notification message
                - type: Notification type (info, warning, error)
                - target: Target audience (all, faculty, admin, etc.)
            
        Returns:
            bool: True if the message was published successfully
        """
        topic = 'consultease/notifications'
        payload = json.dumps({
            **notification_data,
            'timestamp': datetime.now().isoformat()
        })
        
        return self.publish(topic, payload, qos=1)
        
    def publish(self, topic, payload, qos=0, retain=False):
        """
        Publish a message to the MQTT broker.
        
        Args:
            topic (str): MQTT topic
            payload (str or dict): Message payload
            qos (int, optional): Quality of Service level
            retain (bool, optional): Whether the message should be retained
            
        Returns:
            bool: True if the message was published successfully
        """
        # Convert dict payload to JSON string
        if isinstance(payload, dict):
            payload = json.dumps(payload)
            
        # If not connected, queue the message for later
        if not self.connected or not self.client:
            if len(self.message_queue) < self.max_queue_size:
                self.message_queue.append({
                'topic': topic,
                'payload': payload,
                    'qos': qos,
                    'retain': retain
            })
                self.logger.info(f"Queued message for topic {topic} (not connected)")
            else:
                self.logger.warning(f"Message queue full, discarding message for topic {topic}")
            return False
            
        try:
            result = self.client.publish(topic, payload, qos, retain)
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                self.logger.warning(f"Failed to publish message to {topic}: {result.rc}")
                return False
                
            self.logger.debug(f"Published message to {topic}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error publishing message to {topic}: {e}")
            return False
