#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Office Repository

This module provides database operations for office data.
"""

import logging
import sqlite3
from datetime import datetime

from central_system.data.database.database_manager import DatabaseManager
from central_system.data.models.office import Office


class OfficeRepository:
    """Repository for office data in the database."""

    def __init__(self, db_manager=None):
        """
        Initialize the office repository.
        
        Args:
            db_manager (DatabaseManager, optional): Database manager instance
        """
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager or DatabaseManager()
        self._ensure_table()

    def _ensure_table(self):
        """Ensure that the offices table exists in the database."""
        try:
            query = """
            CREATE TABLE IF NOT EXISTS offices (
                office_id TEXT PRIMARY KEY,
                name TEXT,
                building TEXT NOT NULL,
                floor INTEGER DEFAULT 1,
                room TEXT NOT NULL,
                ble_beacon_id TEXT,
                status TEXT DEFAULT 'Active',
                last_updated TEXT
            )
            """
            self.db_manager.execute_query(query)
            self.logger.info("Offices table initialized")
        except sqlite3.Error as error:
            self.logger.error(f"Error ensuring offices table: {error}")
            raise

    def get_all(self):
        """
        Get all offices from the database.
        
        Returns:
            list: List of Office objects
        """
        try:
            query = "SELECT * FROM offices ORDER BY building, floor, room"
            result = self.db_manager.execute_query(query)
            
            offices = []
            for row in result:
                office_data = {
                    'office_id': row[0],
                    'name': row[1],
                    'building': row[2],
                    'floor': row[3],
                    'room': row[4],
                    'ble_beacon_id': row[5],
                    'status': row[6],
                    'last_updated': row[7]
                }
                offices.append(Office(office_data))
            
            return offices
        except sqlite3.Error as error:
            self.logger.error(f"Error getting all offices: {error}")
            return []

    def get_by_id(self, office_id):
        """
        Get an office by its ID.
        
        Args:
            office_id (str): Office ID
            
        Returns:
            Office: Office object if found, None otherwise
        """
        try:
            query = "SELECT * FROM offices WHERE office_id = ?"
            result = self.db_manager.execute_query(query, (office_id,))
            
            if result and len(result) > 0:
                row = result[0]
                office_data = {
                    'office_id': row[0],
                    'name': row[1],
                    'building': row[2],
                    'floor': row[3],
                    'room': row[4],
                    'ble_beacon_id': row[5],
                    'status': row[6],
                    'last_updated': row[7]
                }
                return Office(office_data)
            return None
        except sqlite3.Error as error:
            self.logger.error(f"Error getting office by ID: {error}")
            return None

    def save(self, office):
        """
        Save an office to the database.
        
        Args:
            office (Office): Office object to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update the last_updated timestamp
            office.last_updated = datetime.now().isoformat()
            
            # Check if the office already exists
            existing = self.get_by_id(office.office_id)
            
            if existing:
                # Update existing office
                query = """
                UPDATE offices
                SET name = ?, building = ?, floor = ?, room = ?, 
                    ble_beacon_id = ?, status = ?, last_updated = ?
                WHERE office_id = ?
                """
                params = (
                    office.name,
                    office.building,
                    office.floor,
                    office.room,
                    office.ble_beacon_id,
                    office.status,
                    office.last_updated,
                    office.office_id
                )
            else:
                # Insert new office
                query = """
                INSERT INTO offices (
                    office_id, name, building, floor, room, 
                    ble_beacon_id, status, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    office.office_id,
                    office.name,
                    office.building,
                    office.floor,
                    office.room,
                    office.ble_beacon_id,
                    office.status,
                    office.last_updated
                )
            
            self.db_manager.execute_query(query, params)
            return True
        except sqlite3.Error as error:
            self.logger.error(f"Error saving office: {error}")
            return False

    def delete(self, office_id):
        """
        Delete an office from the database.
        
        Args:
            office_id (str): Office ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = "DELETE FROM offices WHERE office_id = ?"
            self.db_manager.execute_query(query, (office_id,))
            return True
        except sqlite3.Error as error:
            self.logger.error(f"Error deleting office: {error}")
            return False

    def search(self, search_term):
        """
        Search for offices matching the search term.
        
        Args:
            search_term (str): Search term
            
        Returns:
            list: List of matching Office objects
        """
        try:
            # Create search pattern for SQLite LIKE operator
            pattern = f"%{search_term}%"
            
            query = """
            SELECT * FROM offices
            WHERE office_id LIKE ? OR name LIKE ? OR building LIKE ? OR room LIKE ?
            ORDER BY building, floor, room
            """
            result = self.db_manager.execute_query(
                query, (pattern, pattern, pattern, pattern)
            )
            
            offices = []
            for row in result:
                office_data = {
                    'office_id': row[0],
                    'name': row[1],
                    'building': row[2],
                    'floor': row[3],
                    'room': row[4],
                    'ble_beacon_id': row[5],
                    'status': row[6],
                    'last_updated': row[7]
                }
                offices.append(Office(office_data))
            
            return offices
        except sqlite3.Error as error:
            self.logger.error(f"Error searching offices: {error}")
            return []

    def filter_by_status(self, status):
        """
        Filter offices by status.
        
        Args:
            status (str): Status to filter by
            
        Returns:
            list: List of Office objects with the specified status
        """
        try:
            query = "SELECT * FROM offices WHERE status = ? ORDER BY building, floor, room"
            result = self.db_manager.execute_query(query, (status,))
            
            offices = []
            for row in result:
                office_data = {
                    'office_id': row[0],
                    'name': row[1],
                    'building': row[2],
                    'floor': row[3],
                    'room': row[4],
                    'ble_beacon_id': row[5],
                    'status': row[6],
                    'last_updated': row[7]
                }
                offices.append(Office(office_data))
            
            return offices
        except sqlite3.Error as error:
            self.logger.error(f"Error filtering offices by status: {error}")
            return []

    def filter_by_building(self, building):
        """
        Filter offices by building.
        
        Args:
            building (str): Building to filter by
            
        Returns:
            list: List of Office objects in the specified building
        """
        try:
            query = "SELECT * FROM offices WHERE building = ? ORDER BY floor, room"
            result = self.db_manager.execute_query(query, (building,))
            
            offices = []
            for row in result:
                office_data = {
                    'office_id': row[0],
                    'name': row[1],
                    'building': row[2],
                    'floor': row[3],
                    'room': row[4],
                    'ble_beacon_id': row[5],
                    'status': row[6],
                    'last_updated': row[7]
                }
                offices.append(Office(office_data))
            
            return offices
        except sqlite3.Error as error:
            self.logger.error(f"Error filtering offices by building: {error}")
            return []

    def get_buildings(self):
        """
        Get a list of all buildings.
        
        Returns:
            list: List of building names
        """
        try:
            query = "SELECT DISTINCT building FROM offices ORDER BY building"
            result = self.db_manager.execute_query(query)
            
            buildings = [row[0] for row in result]
            return buildings
        except sqlite3.Error as error:
            self.logger.error(f"Error getting buildings: {error}")
            return []

    def get_by_beacon_id(self, beacon_id):
        """
        Get an office by its BLE beacon ID.
        
        Args:
            beacon_id (str): BLE beacon ID
            
        Returns:
            Office: Office object if found, None otherwise
        """
        try:
            query = "SELECT * FROM offices WHERE ble_beacon_id = ?"
            result = self.db_manager.execute_query(query, (beacon_id,))
            
            if result and len(result) > 0:
                row = result[0]
                office_data = {
                    'office_id': row[0],
                    'name': row[1],
                    'building': row[2],
                    'floor': row[3],
                    'room': row[4],
                    'ble_beacon_id': row[5],
                    'status': row[6],
                    'last_updated': row[7]
                }
                return Office(office_data)
            return None
        except sqlite3.Error as error:
            self.logger.error(f"Error getting office by beacon ID: {error}")
            return None 