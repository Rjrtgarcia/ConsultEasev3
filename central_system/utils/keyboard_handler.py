#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Keyboard Handler

This module provides support for on-screen keyboard functionality,
specifically for Squeekboard on Linux-based systems.
"""

import os
import subprocess
import sys
import time
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, Qt
from PyQt6.QtWidgets import QApplication, QLineEdit, QTextEdit, QWidget

from utils.logger import get_logger

class KeyboardHandler(QObject):
    """
    Handler for on-screen keyboard integration.
    
    This class manages the automatic display and hiding of the on-screen keyboard
    when input widgets receive or lose focus.
    """
    
    keyboard_shown = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        """
        Initialize the keyboard handler.
        
        Args:
            parent (QObject, optional): Parent object
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        
        # Check if keyboard is enabled in config
        self.enabled = os.getenv("TOUCHSCREEN_ENABLED", "False").lower() == "true"
        self.keyboard_type = os.getenv("KEYBOARD_TYPE", "squeekboard").lower()
        
        # Get platform
        self.platform = sys.platform
        
        # Keyboard process
        self.keyboard_process = None
        self.is_keyboard_visible = False
        
        # Timer for delayed keyboard hide (to prevent flicker)
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self._hide_keyboard)
        
        self.logger.info(f"Keyboard handler initialized (enabled: {self.enabled}, type: {self.keyboard_type})")
        
    def install_event_filter(self, app):
        """
        Install event filter on application to monitor focus changes.
        
        Args:
            app (QApplication): Application instance
        """
        if not self.enabled:
            return
            
        app.focusChanged.connect(self._handle_focus_change)
        self.logger.info("Event filter installed for keyboard handling")
        
    def _handle_focus_change(self, old, now):
        """
        Handle focus change events.
        
        Args:
            old (QWidget): Widget that lost focus
            now (QWidget): Widget that gained focus
        """
        if not self.enabled:
            return
            
        # Show keyboard when text input widgets get focus
        if now is not None and self._is_text_input(now):
            self._show_keyboard()
        
        # Hide keyboard when non-text widgets get focus
        elif old is not None and not now is None and not self._is_text_input(now):
            # Use timer to prevent keyboard flicker when switching between inputs
            self.hide_timer.start(500)  # 500ms delay before hiding
            
    def _is_text_input(self, widget):
        """
        Check if widget is a text input widget.
        
        Args:
            widget (QWidget): Widget to check
            
        Returns:
            bool: True if widget is a text input
        """
        return isinstance(widget, (QLineEdit, QTextEdit)) or (
            hasattr(widget, 'inherits') and (
                widget.inherits('QLineEdit') or 
                widget.inherits('QTextEdit') or
                widget.inherits('QPlainTextEdit')
            )
        )
            
    def _show_keyboard(self):
        """Show the on-screen keyboard."""
        if self.is_keyboard_visible:
            return
            
        self.hide_timer.stop()  # Cancel any pending hide
        
        if self.platform.startswith('linux'):
            if self.keyboard_type == "squeekboard":
                try:
                    # Use D-Bus to control Squeekboard
                    subprocess.Popen([
                        "busctl", "--user", "call", 
                        "sm.puri.OSK0", "/sm/puri/OSK0", 
                        "sm.puri.OSK0", "SetVisible", "b", "true"
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    self.is_keyboard_visible = True
                    self.keyboard_shown.emit(True)
                    self.logger.info("Squeekboard shown")
                except Exception as e:
                    self.logger.error(f"Error showing Squeekboard: {e}")
            
            elif self.keyboard_type == "onboard":
                try:
                    if not self.keyboard_process:
                        self.keyboard_process = subprocess.Popen(
                            ["onboard", "--xid"], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE
                        )
                    else:
                        # Show existing instance
                        subprocess.Popen(
                            ["dbus-send", "--type=method_call", "--dest=org.onboard.Onboard", 
                             "/org/onboard/Onboard/Keyboard", "org.onboard.Onboard.Keyboard.Show"],
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE
                        )
                        
                    self.is_keyboard_visible = True
                    self.keyboard_shown.emit(True)
                    self.logger.info("Onboard keyboard shown")
                except Exception as e:
                    self.logger.error(f"Error showing Onboard keyboard: {e}")
                    
        else:
            self.logger.warning(f"On-screen keyboard not supported on {self.platform}")
        
    def _hide_keyboard(self):
        """Hide the on-screen keyboard."""
        if not self.is_keyboard_visible:
            return
            
        if self.platform.startswith('linux'):
            if self.keyboard_type == "squeekboard":
                try:
                    # Use D-Bus to control Squeekboard
                    subprocess.Popen([
                        "busctl", "--user", "call", 
                        "sm.puri.OSK0", "/sm/puri/OSK0", 
                        "sm.puri.OSK0", "SetVisible", "b", "false"
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    self.is_keyboard_visible = False
                    self.keyboard_shown.emit(False)
                    self.logger.info("Squeekboard hidden")
                except Exception as e:
                    self.logger.error(f"Error hiding Squeekboard: {e}")
            
            elif self.keyboard_type == "onboard":
                try:
                    # Hide Onboard keyboard
                    subprocess.Popen(
                        ["dbus-send", "--type=method_call", "--dest=org.onboard.Onboard", 
                         "/org/onboard/Onboard/Keyboard", "org.onboard.Onboard.Keyboard.Hide"],
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE
                    )
                    
                    self.is_keyboard_visible = False
                    self.keyboard_shown.emit(False)
                    self.logger.info("Onboard keyboard hidden")
                except Exception as e:
                    self.logger.error(f"Error hiding Onboard keyboard: {e}")
                    
        else:
            self.logger.warning(f"On-screen keyboard not supported on {self.platform}")
            
    def cleanup(self):
        """Clean up resources."""
        if self.platform.startswith('linux') and self.keyboard_type == "onboard" and self.keyboard_process:
            try:
                self.keyboard_process.terminate()
                self.keyboard_process = None
                self.logger.info("Onboard keyboard process terminated")
            except Exception as e:
                self.logger.error(f"Error terminating Onboard keyboard process: {e}")
                
        self.hide_timer.stop() 