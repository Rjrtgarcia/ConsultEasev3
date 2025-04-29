#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Office Model

This module defines the Office model for the ConsultEase application.
"""

from PyQt5.QtCore import QObject, pyqtSignal


class Office(QObject):
    """
    Class representing an Office in the ConsultEase system.
    
    Attributes:
        office_id (str): Unique identifier for the office
        name (str): Name of the office
        building (str): Building where the office is located
        floor (str): Floor where the office is located
        room (str): Room number
        ble_beacon_id (str): Bluetooth Low Energy beacon identifier
        status (str): Current status of the office (active, inactive, maintenance)
        last_updated (str): Timestamp of the last update
    """
    
    # Signal emitted when any data in the model changes
    data_changed = pyqtSignal()
    
    def __init__(self, office_id=None, name=None, building=None, floor=None, 
                 room=None, ble_beacon_id=None, status="inactive", last_updated=None):
        """
        Initialize a new Office instance.
        
        Args:
            office_id (str, optional): Unique identifier for the office
            name (str, optional): Name of the office
            building (str, optional): Building where the office is located
            floor (str, optional): Floor where the office is located
            room (str, optional): Room number
            ble_beacon_id (str, optional): Bluetooth Low Energy beacon identifier
            status (str, optional): Current status of the office (active, inactive, maintenance)
            last_updated (str, optional): Timestamp of the last update
        """
        super().__init__()
        
        self._office_id = office_id
        self._name = name
        self._building = building
        self._floor = floor
        self._room = room
        self._ble_beacon_id = ble_beacon_id
        self._status = status
        self._last_updated = last_updated
    
    @property
    def office_id(self):
        """Get the office ID."""
        return self._office_id
    
    @office_id.setter
    def office_id(self, value):
        """Set the office ID and emit signal."""
        if self._office_id != value:
            self._office_id = value
            self.data_changed.emit()
    
    @property
    def name(self):
        """Get the office name."""
        return self._name
    
    @name.setter
    def name(self, value):
        """Set the office name and emit signal."""
        if self._name != value:
            self._name = value
            self.data_changed.emit()
    
    @property
    def building(self):
        """Get the building name."""
        return self._building
    
    @building.setter
    def building(self, value):
        """Set the building name and emit signal."""
        if self._building != value:
            self._building = value
            self.data_changed.emit()
    
    @property
    def floor(self):
        """Get the floor."""
        return self._floor
    
    @floor.setter
    def floor(self, value):
        """Set the floor and emit signal."""
        if self._floor != value:
            self._floor = value
            self.data_changed.emit()
    
    @property
    def room(self):
        """Get the room number."""
        return self._room
    
    @room.setter
    def room(self, value):
        """Set the room number and emit signal."""
        if self._room != value:
            self._room = value
            self.data_changed.emit()
    
    @property
    def ble_beacon_id(self):
        """Get the BLE beacon ID."""
        return self._ble_beacon_id
    
    @ble_beacon_id.setter
    def ble_beacon_id(self, value):
        """Set the BLE beacon ID and emit signal."""
        if self._ble_beacon_id != value:
            self._ble_beacon_id = value
            self.data_changed.emit()
    
    @property
    def status(self):
        """Get the office status."""
        return self._status
    
    @status.setter
    def status(self, value):
        """Set the office status and emit signal."""
        if self._status != value:
            self._status = value
            self.data_changed.emit()
    
    @property
    def last_updated(self):
        """Get the last updated timestamp."""
        return self._last_updated
    
    @last_updated.setter
    def last_updated(self, value):
        """Set the last updated timestamp and emit signal."""
        if self._last_updated != value:
            self._last_updated = value
            self.data_changed.emit()
    
    def get_location_string(self):
        """
        Get a formatted string representing the office location.
        
        Returns:
            str: A formatted location string (Building, Floor, Room)
        """
        parts = []
        
        if self.building:
            parts.append(self.building)
        
        if self.floor:
            parts.append(f"Floor {self.floor}")
        
        if self.room:
            parts.append(f"Room {self.room}")
        
        if parts:
            return ", ".join(parts)
        else:
            return "Location not specified"
    
    def to_dict(self):
        """
        Convert the office to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the office
        """
        return {
            'office_id': self.office_id,
            'name': self.name,
            'building': self.building,
            'floor': self.floor,
            'room': self.room,
            'ble_beacon_id': self.ble_beacon_id,
            'status': self.status,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an Office instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing office data
            
        Returns:
            Office: A new Office instance
        """
        return cls(
            office_id=data.get('office_id'),
            name=data.get('name'),
            building=data.get('building'),
            floor=data.get('floor'),
            room=data.get('room'),
            ble_beacon_id=data.get('ble_beacon_id'),
            status=data.get('status', 'inactive'),
            last_updated=data.get('last_updated')
        )
    
    def __str__(self):
        """
        Get a string representation of the office.
        
        Returns:
            str: String representation of the office
        """
        return f"Office(id={self.office_id}, name={self.name}, location={self.get_location_string()}, status={self.status})" 