#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - RFID Reader Interface

This module provides an interface for RFID card readers.
It supports both real RFID readers and simulation mode.
"""

import os
import time
import threading
import random
import queue
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from utils.logger import get_logger

# Try to import USB library, but don't fail if not available
try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False

# Try to import evdev for Linux devices
try:
    import evdev
    from evdev import categorize, ecodes
    EVDEV_AVAILABLE = True
except ImportError:
    EVDEV_AVAILABLE = False

class RFIDReaderThread(QThread):
    """
    Thread for reading RFID cards.
    """
    card_detected = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, vendor_id=None, product_id=None, simulate=False):
        """
        Initialize the RFID reader thread.
        
        Args:
            vendor_id (int, optional): USB vendor ID
            product_id (int, optional): USB product ID
            simulate (bool, optional): Whether to simulate RFID reader
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.simulate = simulate
        self.running = False
        self.device = None
        self.evdev_device = None
        self.platform = os.name  # 'posix' for Linux/Mac, 'nt' for Windows
        
        # Buffer for RFID data
        self.buffer = ""
        self.buffer_timeout = QTimer()
        self.buffer_timeout.setInterval(500)  # 500ms timeout for reading
        self.buffer_timeout.timeout.connect(self._reset_buffer)
        
        # Reset detection flag
        self.last_detection_time = 0
        self.detection_cooldown = 2  # seconds
        
    def run(self):
        """Thread main function."""
        self.running = True
        
        if self.simulate:
            self.status_changed.emit("Simulation mode")
            self._run_simulation()
        else:
            # Try different reader types in sequence
            try:
                # First try USB HID readers
                if USB_AVAILABLE:
                    try:
                        self._connect_usb_reader()
                        self._run_usb_reader()
                        return
                    except Exception as e:
                        self.logger.warning(f"USB reader connection failed: {e}")
                
                # Then try evdev (Linux only)
                if EVDEV_AVAILABLE and self.platform == 'posix':
                    try:
                        self._connect_evdev_reader()
                        self._run_evdev_reader()
                        return
                    except Exception as e:
                        self.logger.warning(f"Evdev reader connection failed: {e}")
                
                # If all methods fail, fall back to simulation
                raise Exception("No compatible RFID reader found")
                
            except Exception as e:
                self.logger.error(f"RFID reader error: {e}")
                self.error_occurred.emit(f"Error: {e}")
                self.status_changed.emit("Falling back to simulation mode")
                self._run_simulation()
                
    def stop(self):
        """Stop the thread."""
        self.running = False
        self.buffer_timeout.stop()
        
    def _reset_buffer(self):
        """Reset the RFID data buffer after timeout."""
        if self.buffer:
            self.logger.debug(f"Buffer timeout, resetting buffer: {self.buffer}")
            self.buffer = ""
        self.buffer_timeout.stop()
        
    def _connect_usb_reader(self):
        """Connect to the RFID reader device via USB."""
        if not USB_AVAILABLE:
            self.logger.warning("USB library not available")
            self.status_changed.emit("USB library not available")
            raise ImportError("USB library not available")
            
        # Find the RFID reader device
        if self.vendor_id and self.product_id:
            self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
        else:
            # Try to find a common RFID reader if not specified
            common_readers = [
                {"vendor": 0x08FF, "product": 0x0009},  # ACS ACR122U
                {"vendor": 0x04E6, "product": 0x5591},  # SCM Microsystems
                {"vendor": 0x1FC9, "product": 0x0120},  # NXP
                {"vendor": 0xFFFF, "product": 0x0035},  # Generic HID RFID Reader
                {"vendor": 0x0C27, "product": 0x3BFA},  # Sycreader RFID
                {"vendor": 0x0403, "product": 0x6001}   # FTDI-based readers
            ]
            
            for reader in common_readers:
                self.device = usb.core.find(idVendor=reader["vendor"], idProduct=reader["product"])
                if self.device:
                    self.vendor_id = reader["vendor"]
                    self.product_id = reader["product"]
                    break
        
        if not self.device:
            self.logger.warning("No USB RFID reader found")
            self.status_changed.emit("No USB reader found")
            raise Exception("No USB RFID reader found")
            
        self.logger.info(f"USB RFID reader found: {self.vendor_id:04x}:{self.product_id:04x}")
        self.status_changed.emit("USB Reader connected")
        
        # Configure device
        try:
            # Reset the device
            if self.device.is_kernel_driver_active(0):
                self.device.detach_kernel_driver(0)
                
            # Set configuration
            self.device.set_configuration()
            
            # Get endpoint for reading
            cfg = self.device.get_active_configuration()
            intf = cfg[(0,0)]
            
            self.endpoint = None
            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    self.endpoint = ep
                    break
                    
            if not self.endpoint:
                raise Exception("Could not find input endpoint")
            
        except Exception as e:
            self.logger.error(f"Error configuring USB RFID reader: {e}")
            self.status_changed.emit("USB Configuration error")
            raise
            
    def _connect_evdev_reader(self):
        """Connect to the RFID reader using evdev (Linux only)."""
        if not EVDEV_AVAILABLE:
            self.logger.warning("Evdev library not available")
            self.status_changed.emit("Evdev library not available")
            raise ImportError("Evdev library not available")
            
        # Find devices that might be RFID readers (keyboards)
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        
        # Look for device with "RFID" or "Reader" in the name
        for device in devices:
            name = device.name.lower()
            if ("rfid" in name or "reader" in name or "card" in name or 
                "hid" in name or "keyboard" in name):
                self.evdev_device = device
                self.logger.info(f"Found potential RFID reader: {device.name}")
                break
                
        if not self.evdev_device:
            self.logger.warning("No evdev RFID reader found")
            self.status_changed.emit("No evdev reader found")
            raise Exception("No evdev RFID reader found")
            
        self.logger.info(f"Evdev RFID reader found: {self.evdev_device.name}")
        self.status_changed.emit(f"Evdev Reader connected: {self.evdev_device.name}")
            
    def _run_usb_reader(self):
        """
        Run the USB RFID reader in a loop.
        """
        self.logger.info("Starting USB RFID reader loop")
        self.status_changed.emit("Ready to scan (USB)")
        
        # Setup for reading
        timeout = 100  # ms
        buffer = ""
        
        while self.running:
            try:
                # Read data from the endpoint
                try:
                    data = self.endpoint.read(self.endpoint.wMaxPacketSize, timeout)
                    if data:
                        # Most RFID readers act as HID keyboards
                        # The data format depends on the reader, but often follows USB HID keyboard format
                        char = self._decode_hid_keycode(data)
                        if char:
                            # Start timeout to detect end of scan
                            if not self.buffer_timeout.isActive():
                                self.buffer_timeout.start()
                                
                            # Add character to buffer
                            self.buffer += char
                            
                            # If end of scan detected (often CR or LF)
                            if char == '\n' or char == '\r':
                                self._process_rfid_code(self.buffer.strip())
                                self.buffer = ""
                                self.buffer_timeout.stop()
                except usb.core.USBError as e:
                    if e.errno != 110:  # Timeout error is normal
                        raise
                
                time.sleep(0.01)  # Small sleep to prevent CPU hogging
                
            except Exception as e:
                if self.running:  # Only log if we're still supposed to be running
                    self.logger.error(f"Error reading from USB RFID reader: {e}")
                    self.error_occurred.emit(f"Reading error: {e}")
                    time.sleep(1)  # Wait before retrying
                    
    def _run_evdev_reader(self):
        """
        Run the evdev RFID reader in a loop (Linux only).
        """
        self.logger.info("Starting evdev RFID reader loop")
        self.status_changed.emit("Ready to scan (evdev)")
        
        # Set device to non-blocking mode
        self.evdev_device.grab()
        
        while self.running:
            try:
                # Read events from the device
                for event in self.evdev_device.read_loop():
                    if not self.running:
                        break
                        
                    if event.type == ecodes.EV_KEY:
                        key_event = categorize(event)
                        
                        # Only process key down events
                        if key_event.keystate == key_event.key_down:
                            key_char = self._decode_evdev_keycode(key_event.keycode)
                            
                            if key_char:
                                # Start timeout to detect end of scan
                                if not self.buffer_timeout.isActive():
                                    self.buffer_timeout.start()
                                    
                                # Add character to buffer
                                self.buffer += key_char
                                
                                # If end of scan detected (often Enter key)
                                if key_char == '\n' or key_char == '\r':
                                    self._process_rfid_code(self.buffer.strip())
                                    self.buffer = ""
                                    self.buffer_timeout.stop()
                                    
            except (IOError, OSError) as e:
                if self.running:  # Only log if we're still supposed to be running
                    self.logger.error(f"Error reading from evdev RFID reader: {e}")
                    self.error_occurred.emit(f"Reading error: {e}")
                    time.sleep(1)  # Wait before retrying
                    
            except Exception as e:
                if self.running:
                    self.logger.error(f"Unexpected error in evdev reader: {e}")
                    self.error_occurred.emit(f"Reader error: {e}")
                    time.sleep(1)
                    
        # Release device when done
        try:
            self.evdev_device.ungrab()
        except:
            pass
            
    def _decode_hid_keycode(self, data):
        """
        Decode HID keyboard data to character.
        This is a simplified implementation - actual decoding depends on the reader's format.
        
        Args:
            data (array): USB HID data
            
        Returns:
            str: Decoded character or empty string
        """
        # Simple implementation for common RFID readers that act as keyboards
        # Actual implementation depends on the specific reader's format
        
        # Skip empty or malformed data
        if len(data) < 2:
            return ""
            
        # Common format: byte 0 is modifier, byte 2 is key code
        key_code = data[2] if len(data) > 2 else 0
        
        # Simple mapping for common ASCII characters
        # This is a basic implementation and may need to be customized
        key_map = {
            0x04: 'a', 0x05: 'b', 0x06: 'c', 0x07: 'd', 0x08: 'e',
            0x09: 'f', 0x0A: 'g', 0x0B: 'h', 0x0C: 'i', 0x0D: 'j',
            0x0E: 'k', 0x0F: 'l', 0x10: 'm', 0x11: 'n', 0x12: 'o',
            0x13: 'p', 0x14: 'q', 0x15: 'r', 0x16: 's', 0x17: 't',
            0x18: 'u', 0x19: 'v', 0x1A: 'w', 0x1B: 'x', 0x1C: 'y',
            0x1D: 'z', 0x1E: '1', 0x1F: '2', 0x20: '3', 0x21: '4',
            0x22: '5', 0x23: '6', 0x24: '7', 0x25: '8', 0x26: '9',
            0x27: '0', 0x28: '\n', 0x2C: ' '
        }
        
        # Check if key code is in our map
        if key_code in key_map:
            # Handle shift key (modifier bit 1)
            if data[0] & 0x02 and key_code >= 0x04 and key_code <= 0x1D:
                return key_map[key_code].upper()
            return key_map[key_code]
            
        return ""
        
    def _decode_evdev_keycode(self, keycode):
        """
        Decode evdev keycode to character.
        
        Args:
            keycode (str): Evdev keycode (e.g., 'KEY_A')
            
        Returns:
            str: Decoded character or empty string
        """
        # Remove 'KEY_' prefix
        if keycode.startswith('KEY_'):
            key = keycode[4:]
        else:
            return ""
            
        # Map common keys
        if len(key) == 1 and key.isalnum():
            return key.lower()
        elif key == 'SPACE':
            return ' '
        elif key == 'ENTER':
            return '\n'
        elif key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return key
        elif key == 'DOT':
            return '.'
        elif key == 'MINUS':
            return '-'
            
        return ""
            
    def _process_rfid_code(self, rfid_code):
        """
        Process a complete RFID code.
        
        Args:
            rfid_code (str): RFID code
        """
        # Clean up code (remove any non-alphanumeric chars except common separators)
        cleaned_code = ''.join(c for c in rfid_code if c.isalnum() or c in ':-.')
        
        if not cleaned_code:
            return
            
        # Check for detection cooldown to prevent duplicate reads
        current_time = time.time()
        if current_time - self.last_detection_time < self.detection_cooldown:
            self.logger.debug(f"Ignoring duplicate RFID read: {cleaned_code}")
            return
            
        self.last_detection_time = current_time
        
        self.logger.info(f"RFID card detected: {cleaned_code}")
        self.card_detected.emit(cleaned_code)
            
    def _run_simulation(self):
        """Run RFID reader simulation."""
        self.logger.info("Running RFID reader simulation")
        
        # Sample RFID IDs for simulation
        sample_ids = ["A1B2C3D4", "E5F6G7H8", "I9J0K1L2"]
        
        # Check if we should use deterministic mode for testing
        test_mode = os.getenv("RFID_TEST_MODE", "False").lower() == "true"
        test_id = os.getenv("RFID_TEST_ID", "")
        
        while self.running:
            # In test mode, emit the test ID if provided
            if test_mode and test_id:
                self.card_detected.emit(test_id)
                time.sleep(5)  # Wait before emitting again
                continue
                
            # Randomly simulate an RFID scan every 10-30 seconds
            wait_time = random.randint(10, 30)
            for _ in range(wait_time):
                if not self.running:
                    break
                time.sleep(1)
                
            if self.running:
                # If not in test mode, pick a random ID
                rfid_id = random.choice(sample_ids)
                self.logger.info(f"Simulated RFID scan: {rfid_id}")
                self.card_detected.emit(rfid_id)

class HybridRFIDReader(QObject):
    """
    Hybrid RFID reader class that supports both real hardware and simulation.
    
    Signals:
        card_detected (str): Emitted when an RFID card is detected
        status_changed (str): Emitted when the reader status changes
        error_occurred (str): Emitted when an error occurs
    """
    card_detected = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        Initialize the RFID reader.
        
        Args:
            parent (QObject, optional): Parent object
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        
        # Check if simulation mode is enabled
        self.simulation_mode = os.getenv("RFID_SIMULATION_MODE", "False").lower() == "true"
        
        # Get vendor and product IDs from environment if available
        vendor_id_str = os.getenv("RFID_VENDOR_ID", "")
        product_id_str = os.getenv("RFID_PRODUCT_ID", "")
        
        self.vendor_id = int(vendor_id_str, 16) if vendor_id_str else None
        self.product_id = int(product_id_str, 16) if product_id_str else None
        
        # Create reader thread
        self.reader_thread = None
        
        # Queue for detected RFID card IDs
        self.rfid_queue = queue.Queue()
        
        # Recent detections to prevent duplicates
        self.recent_detections = {}
        self.detection_timeout = 5  # seconds

    def start_detection(self):
        """Start RFID detection."""
        if self.reader_thread and self.reader_thread.isRunning():
            self.logger.warning("RFID reader thread already running")
            return
            
        self.logger.info("Starting RFID detection")
        
        # Create and configure reader thread
        self.reader_thread = RFIDReaderThread(
            vendor_id=self.vendor_id,
            product_id=self.product_id,
            simulate=self.simulation_mode
        )
        
        # Connect signals
        self.reader_thread.card_detected.connect(self._handle_card_detection)
        self.reader_thread.status_changed.connect(self.status_changed)
        self.reader_thread.error_occurred.connect(self.error_occurred)
        
        # Start the thread
        self.reader_thread.start()

    def _handle_card_detection(self, rfid_id):
        """
        Handle card detection events from the reader thread.
        Filters out duplicate reads and emits card_detected signal.
        
        Args:
            rfid_id (str): Detected RFID card ID
        """
        # Check if this is a duplicate detection
        current_time = time.time()
        if rfid_id in self.recent_detections:
            last_detection = self.recent_detections[rfid_id]
            if current_time - last_detection < self.detection_timeout:
                self.logger.debug(f"Ignoring duplicate RFID read: {rfid_id}")
                return
                
        # Update detection time
        self.recent_detections[rfid_id] = current_time
        
        # Clean up old detections
        self.recent_detections = {
            id: timestamp for id, timestamp in self.recent_detections.items()
            if current_time - timestamp < self.detection_timeout
        }
        
        # Add to queue and emit signal
        self.rfid_queue.put(rfid_id)
        self.card_detected.emit(rfid_id)

    def stop_detection(self):
        """Stop RFID detection."""
        if not self.reader_thread or not self.reader_thread.isRunning():
            return
            
        self.logger.info("Stopping RFID detection")
        self.reader_thread.stop()
        self.reader_thread.wait(1000)  # Wait up to 1 second for thread to finish
        
        if self.reader_thread.isRunning():
            self.logger.warning("RFID reader thread did not stop gracefully, terminating")
            self.reader_thread.terminate()

    def simulate_scan(self, rfid_id):
        """
        Simulate an RFID scan.
        
        Args:
            rfid_id (str): RFID card ID to simulate
        """
        if not self.simulation_mode:
            self.logger.warning("Cannot simulate scan in hardware mode")
            return
            
        self.logger.info(f"Simulating RFID scan: {rfid_id}")
        self._handle_card_detection(rfid_id)
