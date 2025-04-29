#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Error Handler

This module provides error handling functionality for the ConsultEase application.
It includes functions for displaying error messages and exception handling.
"""

import sys
import traceback
from PyQt6.QtWidgets import QMessageBox, QApplication
from utils.logger import get_logger

logger = get_logger(__name__)

def setup_exception_handler(debug_mode=False):
    """
    Set up global exception handler to catch unhandled exceptions.
    
    Args:
        debug_mode (bool): Whether to show detailed error information in dialogs
    """
    def exception_handler(exc_type, exc_value, exc_traceback):
        """
        Custom exception handler function.
        
        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
    """
    # Log the exception
        logger.critical("Unhandled exception", 
                      exc_info=(exc_type, exc_value, exc_traceback))
    
        # Get formatted traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = ''.join(tb_lines)
    
    # Show error dialog
        if QApplication.instance():
            error_message = str(exc_value)
            detailed_text = tb_text if debug_mode else None
            
            show_error_dialog(
                title="Unhandled Exception",
                message=f"An unexpected error occurred: {exc_type.__name__}",
                details=error_message,
                detailed_text=detailed_text
            )
    
    # Set the exception handler
    sys.excepthook = exception_handler
    logger.info("Global exception handler installed")

def show_error_dialog(title="Error", message="An error occurred", details=None, detailed_text=None):
    """
    Show an error dialog with the given title and message.
    
    Args:
        title (str): Dialog title
        message (str): Main error message
        details (str): Additional details about the error
        detailed_text (str): Detailed technical information (e.g., traceback)
    """
    # Ensure we have a QApplication instance
    app = QApplication.instance()
    if not app:
        logger.warning("No QApplication instance for error dialog")
        logger.error(f"{title}: {message} - {details}")
        return
    
    # Create the message box
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Icon.Critical)
    error_box.setWindowTitle(title)
    error_box.setText(message)
    
    if details:
        error_box.setInformativeText(details)
        
    if detailed_text:
        error_box.setDetailedText(detailed_text)
    
    # Add standard buttons
    error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    
    # Show the dialog
    error_box.exec()
    
    logger.error(f"Error dialog shown: {title} - {message}")

def show_warning_dialog(title="Warning", message="Warning", details=None):
    """
    Show a warning dialog with the given title and message.
    
    Args:
        title (str): Dialog title
        message (str): Main warning message
        details (str): Additional details about the warning
    """
    # Ensure we have a QApplication instance
    app = QApplication.instance()
    if not app:
        logger.warning("No QApplication instance for warning dialog")
        logger.warning(f"{title}: {message} - {details}")
        return
    
    # Create the message box
    warning_box = QMessageBox()
    warning_box.setIcon(QMessageBox.Icon.Warning)
    warning_box.setWindowTitle(title)
    warning_box.setText(message)
    
    if details:
        warning_box.setInformativeText(details)
    
    # Add standard buttons
    warning_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    
    # Show the dialog
    warning_box.exec()

    logger.warning(f"Warning dialog shown: {title} - {message}")

def show_confirmation_dialog(title="Confirm", message="Are you sure?", details=None):
    """
    Show a confirmation dialog with the given title and message.
    
    Args:
        title (str): Dialog title
        message (str): Main confirmation message
        details (str): Additional details
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    # Ensure we have a QApplication instance
    app = QApplication.instance()
    if not app:
        logger.warning("No QApplication instance for confirmation dialog")
        return False
    
    # Create the message box
    confirm_box = QMessageBox()
    confirm_box.setIcon(QMessageBox.Icon.Question)
    confirm_box.setWindowTitle(title)
    confirm_box.setText(message)
    
    if details:
        confirm_box.setInformativeText(details)
    
    # Add Yes/No buttons
    confirm_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    confirm_box.setDefaultButton(QMessageBox.StandardButton.No)
    
    # Show the dialog and return result
    result = confirm_box.exec()
    
    return result == QMessageBox.StandardButton.Yes
