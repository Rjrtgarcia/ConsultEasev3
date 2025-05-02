#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConsultEase - Admin Panels Package

This package provides admin panel functionality for the ConsultEase application.
"""

from .faculty_manager import FacultyManagerPanel
from .faculty_history_viewer import FacultyHistoryViewer
from .office_manager import OfficeManagerPanel
from .student_manager import StudentManagerPanel
from .request_manager import RequestManagerPanel
from .audit_log_viewer import AuditLogViewerPanel
from .system_settings import SystemSettingsPanel

__all__ = [
    'FacultyManagerPanel',
    'FacultyHistoryViewer',
    'OfficeManagerPanel',
    'StudentManagerPanel',
    'RequestManagerPanel',
    'AuditLogViewerPanel',
    'SystemSettingsPanel'
] 