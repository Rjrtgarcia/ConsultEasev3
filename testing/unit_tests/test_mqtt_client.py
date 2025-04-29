#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - MQTT Client Unit Tests

This module tests the MQTT client functionality, including:
- Connection handling
- Message publishing/subscription
- Reconnection logic
- Message queuing
"""

import os
import time
import json
import unittest
import tempfile
from unittest.mock import MagicMock, patch, call
from datetime import datetime

# Add parent directory to path to allow importing from central_system
import sys
import pathlib
parent_dir = str(pathlib.Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from central_system.data.mqtt_client import MQTTClient


class TestMQTTClient(unittest.TestCase):
    """Test cases for the MQTT client."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for MQTT persistence
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'MQTT_BROKER': 'test.broker.com',
            'MQTT_PORT': '1883',
            'MQTT_CLIENT_ID': 'test-client',
            'MQTT_USERNAME': 'test-user',
            'MQTT_PASSWORD': 'test-password'
        })
        self.env_patcher.start()
        
        # Create patcher for paho.mqtt.client
        self.mqtt_patcher = patch('central_system.data.mqtt_client.mqtt')
        self.mock_mqtt = self.mqtt_patcher.start()
        
        # Create mock client instance
        self.mock_client = MagicMock()
        self.mock_mqtt.Client.return_value = self.mock_client
        
        # Mock constants
        self.mock_mqtt.MQTT_ERR_SUCCESS = 0
        self.mock_mqtt.MQTT_ERR_NO_CONN = 1
        self.mock_mqtt.MQTTv311 = 4
        
        # Create MQTT client instance with test params
        self.mqtt_client = MQTTClient(
            broker='test.broker.com',
            port=1883,
            client_id='test-client',
            username='test-user',
            password='test-password'
        )
        
        # Set up signal handling
        self.connection_changed_called = False
        self.connection_status = None
        
        def on_connection_changed(status):
            self.connection_changed_called = True
            self.connection_status = status
            
        self.mqtt_client.connection_changed.connect(on_connection_changed)
        
        # Reset mocks
        self.mock_client.reset_mock()

    def tearDown(self):
        """Tear down the test environment."""
        # Stop patchers
        self.mqtt_patcher.stop()
        self.env_patcher.stop()
        
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test client initialization with correct parameters."""
        # Verify mqtt.Client was called
        self.mock_mqtt.Client.assert_called_once()
        
        # Verify credentials were set
        self.mock_client.username_pw_set.assert_called_once_with('test-user', 'test-password')
        
        # Verify will message was set
        self.mock_client.will_set.assert_called_once()
        
        # Verify callback registration
        self.assertEqual(self.mock_client.on_connect, self.mqtt_client._on_connect)
        self.assertEqual(self.mock_client.on_disconnect, self.mqtt_client._on_disconnect)
        self.assertEqual(self.mock_client.on_message, self.mqtt_client._on_message)

    def test_connect(self):
        """Test connection to the MQTT broker."""
        # Call connect
        result = self.mqtt_client.connect()
        
        # Verify connect_async was called
        self.mock_client.connect_async.assert_called_once_with('test.broker.com', 1883, keepalive=60)
        
        # Verify loop_start was called
        self.mock_client.loop_start.assert_called_once()
        
        # Verify return value
        self.assertTrue(result)

    def test_disconnect(self):
        """Test disconnection from the MQTT broker."""
        # Set connected state
        self.mqtt_client.connected = True
        
        # Call disconnect
        self.mqtt_client.disconnect()
        
        # Verify loop_stop and disconnect were called
        self.mock_client.loop_stop.assert_called_once()
        self.mock_client.disconnect.assert_called_once()
        
        # Verify connected state changed
        self.assertFalse(self.mqtt_client.connected)
        self.assertTrue(self.connection_changed_called)
        self.assertFalse(self.connection_status)

    def test_on_connect_success(self):
        """Test on_connect callback with successful connection."""
        # Call on_connect with success code (0)
        self.mqtt_client._on_connect(self.mock_client, None, None, 0)
        
        # Verify connected state
        self.assertTrue(self.mqtt_client.connected)
        self.assertTrue(self.connection_changed_called)
        self.assertTrue(self.connection_status)
        
        # Verify topics subscription
        self.assertEqual(self.mock_client.subscribe.call_count, 3)  # 3 topics in self.topics
        
        # Verify first topic subscription
        call_args = self.mock_client.subscribe.call_args_list[0][0]
        self.assertEqual(call_args[0], 'faculty/+/status')
        self.assertEqual(call_args[1], 1)  # QoS

    def test_on_connect_failure(self):
        """Test on_connect callback with connection failure."""
        # Set connected state
        self.mqtt_client.connected = True
        
        # Call on_connect with failure code (1)
        self.mqtt_client._on_connect(self.mock_client, None, None, 1)
        
        # Verify connected state
        self.assertFalse(self.mqtt_client.connected)
        self.assertTrue(self.connection_changed_called)
        self.assertFalse(self.connection_status)

    def test_on_disconnect_unexpected(self):
        """Test on_disconnect callback with unexpected disconnection."""
        # Set connected state
        self.mqtt_client.connected = True
        
        # Mock _start_reconnect_timer
        self.mqtt_client._start_reconnect_timer = MagicMock()
        
        # Call on_disconnect with non-zero rc (unexpected disconnect)
        self.mqtt_client._on_disconnect(self.mock_client, None, 1)
        
        # Verify connected state
        self.assertFalse(self.mqtt_client.connected)
        self.assertTrue(self.connection_changed_called)
        self.assertFalse(self.connection_status)
        
        # Verify reconnect timer was started
        self.mqtt_client._start_reconnect_timer.assert_called_once()

    def test_on_message(self):
        """Test on_message callback."""
        # Mock _process_message
        self.mqtt_client._process_message = MagicMock()
        
        # Create mock message
        mock_msg = MagicMock()
        mock_msg.topic = 'faculty/faculty001/status'
        mock_msg.payload = json.dumps({'status': 'available'}).encode('utf-8')
        
        # Call on_message
        self.mqtt_client._on_message(self.mock_client, None, mock_msg)
        
        # Verify message processing
        self.mqtt_client._process_message.assert_called_once_with(
            'faculty/faculty001/status',
            json.dumps({'status': 'available'})
        )

    def test_process_message_faculty_status(self):
        """Test processing of faculty status message."""
        # Create signal tracking
        received_faculty_id = None
        received_status = None
        
        def on_faculty_status_changed(faculty_id, status):
            nonlocal received_faculty_id, received_status
            received_faculty_id = faculty_id
            received_status = status
            
        self.mqtt_client.faculty_status_changed.connect(on_faculty_status_changed)
        
        # Call _process_message with faculty status message
        topic = 'faculty/faculty001/status'
        payload = json.dumps({'status': 'available'})
        self.mqtt_client._process_message(topic, payload)
        
        # Verify signal was emitted with correct parameters
        self.assertEqual(received_faculty_id, 'faculty001')
        self.assertEqual(received_status, 'available')

    def test_process_message_request(self):
        """Test processing of consultation request message."""
        # Create signal tracking
        received_request = None
        
        def on_request_received(request):
            nonlocal received_request
            received_request = request
            
        self.mqtt_client.request_received.connect(on_request_received)
        
        # Call _process_message with request message
        topic = 'faculty/faculty001/requests'
        payload = json.dumps({
            'student_id': 'student001',
            'subject': 'Test Subject',
            'message': 'Test Message'
        })
        self.mqtt_client._process_message(topic, payload)
        
        # Verify signal was emitted with correct parameters
        self.assertEqual(received_request['faculty_id'], 'faculty001')
        self.assertEqual(received_request['student_id'], 'student001')
        self.assertEqual(received_request['subject'], 'Test Subject')
        self.assertEqual(received_request['message'], 'Test Message')

    def test_process_message_invalid_json(self):
        """Test processing of message with invalid JSON."""
        # Call _process_message with invalid JSON
        topic = 'faculty/faculty001/status'
        payload = '{"status": "available'  # Invalid JSON
        
        # This should not raise an exception
        self.mqtt_client._process_message(topic, payload)

    def test_publish_when_connected(self):
        """Test publishing message when connected."""
        # Set connected state
        self.mqtt_client.connected = True
        
        # Mock successful publish result
        mock_result = MagicMock()
        mock_result.rc = 0  # MQTT_ERR_SUCCESS
        self.mock_client.publish.return_value = mock_result
        
        # Call publish
        result = self.mqtt_client.publish('test/topic', 'test-payload', qos=1, retain=True)
        
        # Verify publish was called
        self.mock_client.publish.assert_called_once_with('test/topic', 'test-payload', 1, True)
        
        # Verify return value
        self.assertTrue(result)

    def test_publish_when_disconnected(self):
        """Test publishing message when disconnected (should queue the message)."""
        # Set disconnected state
        self.mqtt_client.connected = False
        
        # Call publish
        result = self.mqtt_client.publish('test/topic', 'test-payload', qos=1, retain=True)
        
        # Verify publish was not called
        self.mock_client.publish.assert_not_called()
        
        # Verify message was queued
        self.assertEqual(len(self.mqtt_client.message_queue), 1)
        queued_msg = self.mqtt_client.message_queue[0]
        self.assertEqual(queued_msg['topic'], 'test/topic')
        self.assertEqual(queued_msg['payload'], 'test-payload')
        self.assertEqual(queued_msg['qos'], 1)
        self.assertEqual(queued_msg['retain'], True)
        
        # Verify return value
        self.assertFalse(result)

    def test_publish_faculty_status(self):
        """Test publishing faculty status update."""
        # Mock publish method
        self.mqtt_client.publish = MagicMock(return_value=True)
        
        # Call publish_faculty_status
        result = self.mqtt_client.publish_faculty_status('faculty001', 'available')
        
        # Verify publish was called
        self.mqtt_client.publish.assert_called_once()
        call_args = self.mqtt_client.publish.call_args[0]
        self.assertEqual(call_args[0], 'faculty/faculty001/status')
        
        # Parse JSON payload
        payload = json.loads(call_args[1])
        self.assertEqual(payload['status'], 'available')
        self.assertTrue('timestamp' in payload)
        
        # Verify QoS and retain
        call_kwargs = self.mqtt_client.publish.call_args[1]
        self.assertEqual(call_kwargs['qos'], 1)
        self.assertEqual(call_kwargs['retain'], True)
        
        # Verify return value
        self.assertTrue(result)

    def test_process_message_queue(self):
        """Test processing of queued messages."""
        # Set connected state
        self.mqtt_client.connected = True
        
        # Add messages to queue
        self.mqtt_client.message_queue = [
            {'topic': 'test/topic1', 'payload': 'payload1', 'qos': 0, 'retain': False},
            {'topic': 'test/topic2', 'payload': 'payload2', 'qos': 1, 'retain': True}
        ]
        
        # Mock publish method
        self.mqtt_client.publish = MagicMock(return_value=True)
        
        # Call _process_message_queue
        self.mqtt_client._process_message_queue()
        
        # Verify all messages were published
        self.assertEqual(self.mqtt_client.publish.call_count, 2)
        
        # Verify queue was cleared
        self.assertEqual(len(self.mqtt_client.message_queue), 0)
        
        # Verify correct calls
        call_args_list = self.mqtt_client.publish.call_args_list
        self.assertEqual(call_args_list[0][0], ('test/topic1', 'payload1'))
        self.assertEqual(call_args_list[0][1], {'qos': 0, 'retain': False})
        self.assertEqual(call_args_list[1][0], ('test/topic2', 'payload2'))
        self.assertEqual(call_args_list[1][1], {'qos': 1, 'retain': True})

    def test_reconnect_backoff(self):
        """Test reconnection with exponential backoff."""
        # Call _start_reconnect_timer multiple times
        self.mqtt_client._start_reconnect_timer()
        
        # Verify initial reconnect interval
        self.assertEqual(self.mqtt_client.current_reconnect_interval, 10)  # 5 * 2
        
        # Call again
        self.mqtt_client._start_reconnect_timer()
        
        # Verify increased reconnect interval
        self.assertEqual(self.mqtt_client.current_reconnect_interval, 20)  # 10 * 2
        
        # Call until we hit max
        self.mqtt_client._start_reconnect_timer()  # 40
        self.mqtt_client._start_reconnect_timer()  # 80
        self.mqtt_client._start_reconnect_timer()  # 160
        self.mqtt_client._start_reconnect_timer()  # 300 (max)
        
        # Verify max reconnect interval
        self.assertEqual(self.mqtt_client.current_reconnect_interval, 300)  # max
        
        # Call one more time to ensure it doesn't exceed max
        self.mqtt_client._start_reconnect_timer()
        
        # Verify max reconnect interval is still 300
        self.assertEqual(self.mqtt_client.current_reconnect_interval, 300)

    def test_successful_reconnect_resets_interval(self):
        """Test that a successful reconnection resets the backoff interval."""
        # Increase backoff interval
        self.mqtt_client.current_reconnect_interval = 300
        
        # Simulate successful connection
        self.mqtt_client._on_connect(self.mock_client, None, None, 0)
        
        # Verify reset reconnect interval
        self.assertEqual(self.mqtt_client.current_reconnect_interval, self.mqtt_client.reconnect_interval)


if __name__ == '__main__':
    unittest.main() 