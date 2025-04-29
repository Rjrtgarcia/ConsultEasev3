#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Data Models

This module provides data models for the ConsultEase application.
"""

from .faculty import Faculty
from .student import Student
from .consultation_request import ConsultationRequest

__all__ = ['Faculty', 'Student', 'ConsultationRequest']
