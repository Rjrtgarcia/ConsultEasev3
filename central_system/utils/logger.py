#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Logger Utility

This module provides logging functionality for the ConsultEase application.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Default log format
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Create loggers dictionary to store loggers by name
_loggers = {}

def setup_logger(name='consultease', level=logging.INFO, log_file=None, log_format=None):
    """
    Set up a logger with the given name, level, and format.
    
    Args:
        name (str, optional): Logger name. Defaults to 'consultease'.
        level (int, optional): Logging level. Defaults to logging.INFO.
        log_file (str, optional): Path to log file. If None, logs to console only.
        log_format (str, optional): Log format string. Defaults to DEFAULT_LOG_FORMAT.
        
    Returns:
        logging.Logger: Configured logger
    """
    # If logger already exists, return it
    if name in _loggers:
        return _loggers[name]
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(log_format or DEFAULT_LOG_FORMAT)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file provided
    if log_file:
        # Make sure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # Create default log file in logs directory
        logs_dir = Path(__file__).parent.parent / 'logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d')
        default_log_file = logs_dir / f'consultease_{timestamp}.log'
        
        file_handler = logging.FileHandler(default_log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Store logger in dictionary
    _loggers[name] = logger

    return logger

def get_logger(name=None):
    """
    Get a logger by name. If not found, create a new one.
    
    Args:
        name (str, optional): Logger name. If None, uses calling module name.
        
    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        # Get the name of the calling module
        import inspect
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = module.__name__
    
    # If logger exists, return it
    if name in _loggers:
        return _loggers[name]
    
    # If root logger exists, create child logger
    if 'consultease' in _loggers:
        logger = _loggers['consultease'].getChild(name)
        _loggers[name] = logger
        return logger
    
    # Otherwise, create a new logger
    return setup_logger(name)

def set_log_level(level):
    """
    Set the log level for all loggers.
    
    Args:
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG)
    """
    for logger in _loggers.values():
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)
