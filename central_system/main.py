#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Main Application

This is the main entry point for the ConsultEase application.
It initializes the application, sets up logging, connects to the database,
initializes the MQTT client, and launches the login screen.
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import PyQt6 components
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt, QTimer

# Import application modules
from utils.logger import setup_logger
from utils.keyboard_handler import KeyboardHandler
from data.database import DatabaseManager
from data.mqtt_client import MQTTClient
from ui.login_screen import LoginScreen
from ui.styles.style_loader import load_stylesheet
from utils.error_handler import setup_exception_handler, show_error_dialog

def main():
    """
    Main application entry point.
    """
    try:
        # Load environment variables
        env_path = Path(__file__).parent / "config.env"
        load_dotenv(dotenv_path=env_path)
        
        # Setup logging
        log_level = os.getenv("LOG_LEVEL", "INFO")
        debug_mode = os.getenv("DEBUG_MODE", "False").lower() == "true"
        logger = setup_logger(level=getattr(logging, log_level))
    logger.info("Starting ConsultEase application")
    
        # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("ConsultEase")
        app.setApplicationVersion("1.0.0")
    
        # Set application style
        app.setStyle("Fusion")  # Base style
        stylesheet = load_stylesheet("dark.qss")  # Custom stylesheet
        app.setStyleSheet(stylesheet)
        
        # Custom font for touchscreen
        if os.getenv("TOUCHSCREEN_ENABLED", "False").lower() == "true":
            default_font = QFont("Roboto", 12)
            app.setFont(default_font)
        
        # Initialize on-screen keyboard support
        keyboard_enabled = os.getenv("KEYBOARD_ENABLED", "False").lower() == "true"
        keyboard_handler = None
        if keyboard_enabled:
            logger.info("Initializing on-screen keyboard support")
            keyboard_handler = KeyboardHandler()
            keyboard_handler.install_event_filter(app)
        
        # Show splash screen
        splash_path = Path(__file__).parent / "ui" / "assets" / "splash.png"
        if splash_path.exists():
            splash_pixmap = QPixmap(str(splash_path))
            splash = QSplashScreen(splash_pixmap)
            splash.show()
            app.processEvents()
        else:
            splash = None
        
        # Setup exception handler
        setup_exception_handler(debug_mode)
    
    # Initialize database connection
        logger.info("Initializing database connection")
        db_manager = DatabaseManager()
    
    # Initialize MQTT client
        logger.info("Initializing MQTT client")
        mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
        mqtt_client_id = os.getenv("MQTT_CLIENT_ID", "central_system")
        mqtt_username = os.getenv("MQTT_USERNAME", "")
        mqtt_password = os.getenv("MQTT_PASSWORD", "")
        
        # Add MQTT credentials if provided
        mqtt_client = MQTTClient(
            broker=mqtt_broker, 
            port=mqtt_port, 
            client_id=mqtt_client_id,
            username=mqtt_username if mqtt_username else None,
            password=mqtt_password if mqtt_password else None
        )
        
        # Connect to MQTT broker
        mqtt_client.connect()
        
        # Create and show login screen
        logger.info("Launching login screen")
        
        # Wait a moment to show splash screen
        if splash:
            QTimer.singleShot(2000, splash.close)
        
        # Create the login screen
        login = LoginScreen(db_manager, mqtt_client)
        
        # Add keyboard handler to app context for access in other modules
        if keyboard_handler:
            app.keyboard_handler = keyboard_handler
            
        login.show()
        
        # Register cleanup for application exit
        app.aboutToQuit.connect(lambda: cleanup(keyboard_handler))
        
        # Start the application event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}")
        logging.error(traceback.format_exc())
        
        # Show error dialog
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("Critical Error")
        error_msg.setText("An unexpected error has occurred")
        error_msg.setInformativeText(str(e))
        error_msg.setDetailedText(traceback.format_exc())
        error_msg.exec()
        
        sys.exit(1)

def cleanup(keyboard_handler):
    """
    Perform cleanup tasks before application exit.
    
    Args:
        keyboard_handler (KeyboardHandler): Keyboard handler instance
    """
    if keyboard_handler:
        keyboard_handler.cleanup()

if __name__ == "__main__":
    main()
