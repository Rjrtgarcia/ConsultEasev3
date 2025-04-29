#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Style Loader

This module provides functions to load QSS stylesheets for the application UI.
"""

import os
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

def load_stylesheet(stylesheet_name):
    """
    Load a QSS stylesheet by name.
    
    Args:
        stylesheet_name (str): Name of the stylesheet file (e.g., "dark.qss")
        
    Returns:
        str: Contents of the stylesheet, or empty string if not found
    """
    try:
        # Get the path to the styles directory
        styles_dir = Path(__file__).parent
        stylesheet_path = styles_dir / stylesheet_name
        
        # If the file doesn't exist, try to find it in subdirectories
        if not stylesheet_path.exists():
            for subdir in styles_dir.iterdir():
                if subdir.is_dir():
                    potential_path = subdir / stylesheet_name
                    if potential_path.exists():
                        stylesheet_path = potential_path
                        break
        
        # If still not found, return empty string
        if not stylesheet_path.exists():
            logger.warning(f"Stylesheet {stylesheet_name} not found")
            return ""
        
        # Read the stylesheet
        with open(stylesheet_path, 'r', encoding='utf-8') as file:
            stylesheet = file.read()
            
        logger.info(f"Loaded stylesheet: {stylesheet_name}")
        return stylesheet
        
    except Exception as e:
        logger.error(f"Error loading stylesheet {stylesheet_name}: {e}")
        return ""

def get_available_stylesheets():
    """
    Get a list of available stylesheets.
    
    Returns:
        list: List of stylesheet names
    """
    try:
        styles_dir = Path(__file__).parent
        stylesheets = []
        
        # Look for .qss files in the styles directory and subdirectories
        for file in styles_dir.glob("**/*.qss"):
            stylesheets.append(file.name)
            
        return stylesheets
        
    except Exception as e:
        logger.error(f"Error getting available stylesheets: {e}")
        return [] 