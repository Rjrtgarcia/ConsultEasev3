# ConsultEase User Manual

This user manual provides detailed instructions for using the ConsultEase Student-Faculty Interaction System. It covers both the Central System (for students and administrators) and the Faculty Desk Unit.

## Table of Contents

1. [Introduction](#introduction)
2. [Central System - Student Interface](#central-system---student-interface)
   - [RFID Login](#rfid-login)
   - [Main Dashboard](#main-dashboard)
   - [Faculty Availability](#faculty-availability)
   - [Consultation Requests](#consultation-requests)
   - [Notifications](#notifications)
3. [Central System - Admin Interface](#central-system---admin-interface)
   - [Admin Login](#admin-login)
   - [Faculty Management](#faculty-management)
   - [Audit Logs](#audit-logs)
4. [Faculty Desk Unit](#faculty-desk-unit)
   - [Display Overview](#display-overview)
   - [Button Controls](#button-controls)
   - [BLE Presence Detection](#ble-presence-detection)
   - [Handling Consultation Requests](#handling-consultation-requests)
5. [Troubleshooting](#troubleshooting)
   - [Central System Issues](#central-system-issues)
   - [Faculty Desk Unit Issues](#faculty-desk-unit-issues)

## Introduction

ConsultEase is a comprehensive system designed to enhance student-faculty interaction through:

- RFID-based student authentication
- Real-time faculty availability tracking
- Streamlined consultation request management
- BLE-based faculty presence detection

The system consists of two main components:

1. **Central System**: A Raspberry Pi-based application with a PyQt user interface
2. **Faculty Desk Unit**: An ESP32-based device with an OLED display and button controls

## Central System - Student Interface

### RFID Login

The login screen is the entry point to the ConsultEase system for students.

![Login Screen](login_screen_placeholder.png)

**To log in:**

1. Approach the Central System terminal
2. Scan your RFID card by placing it near the RFID reader
3. The system will authenticate your card and display your information
4. Upon successful authentication, you will be directed to the main dashboard

**Manual Login (if available):**

If you don't have an RFID card or it's not working:

1. Click the "Manual Login" button
2. Enter your student ID and password
3. Click "Login" to access the system

### Main Dashboard

The main dashboard provides an overview of faculty availability and allows you to submit consultation requests.

![Main Dashboard](dashboard_placeholder.png)

The dashboard is divided into three main sections:

1. **Faculty Availability Panel** (left)
2. **Consultation Request Form** (top right)
3. **Notifications Panel** (bottom right)

### Faculty Availability

The Faculty Availability panel shows the current status of all faculty members.

**Features:**

- **Status Indicators**:
  - Green: Faculty is available
  - Red: Faculty is unavailable
- **Filtering Options**:
  - Filter by department using the dropdown menu
  - Filter by status (Available/Unavailable)
  - Use the search box to find specific faculty members
- **Faculty Cards**:
  - Display faculty name, department, and office location
  - Show current availability status
  - Update in real-time as faculty status changes

**To filter faculty:**

1. Select a department from the "Department" dropdown
2. Select a status from the "Status" dropdown
3. Or type a faculty name in the search box

### Consultation Requests

The Consultation Request form allows you to submit requests to faculty members.

**To submit a request:**

1. Select a faculty member from the dropdown menu
2. Enter the course code (optional but recommended)
3. Type your request details in the text area
   - Be specific about what you need help with
   - Keep your request concise but informative
4. Click "Submit Request"
5. A confirmation message will appear if the request was successful

**Guidelines for effective requests:**

- Clearly state the purpose of your consultation
- Mention specific topics, questions, or issues
- Include relevant course information
- Be respectful and professional

### Notifications

The Notifications panel displays system messages and updates.

**Types of notifications:**

- Faculty status changes (e.g., "Dr. Smith is now available")
- Request confirmations
- System announcements
- Error messages

Notifications are displayed in chronological order with the most recent at the top.

## Central System - Admin Interface

### Admin Login

The admin interface is accessible from the login screen.

**To access the admin interface:**

1. Click "Admin Login" on the login screen
2. Enter your admin username and password
3. Click "Login"

### Faculty Management

The Faculty Management tab allows administrators to manage faculty information.

![Admin Interface](admin_interface_placeholder.png)

**Features:**

- **Add Faculty**: Add new faculty members to the system
- **Edit Faculty**: Modify existing faculty information
- **Delete Faculty**: Remove faculty members from the system
- **Search**: Find specific faculty members

**To add a faculty member:**

1. Click "Add Faculty"
2. Fill in the required information:
   - Name
   - Department
   - Email
   - Phone (optional)
   - Office location
   - BLE Beacon ID (for presence detection)
   - Initial status
3. Click "Save"

**To edit a faculty member:**

1. Select the faculty member from the table
2. Click "Edit"
3. Modify the information as needed
4. Click "Save"

**To delete a faculty member:**

1. Select the faculty member from the table
2. Click "Delete"
3. Confirm the deletion when prompted

### Audit Logs

The Audit Logs tab displays a record of system activities.

**Information displayed:**

- Timestamp
- Action type
- User ID
- Details of the action

This information is useful for security monitoring and troubleshooting.

## Faculty Desk Unit

### Display Overview

The Faculty Desk Unit features an OLED display that shows:

![Faculty Desk Unit](faculty_unit_placeholder.png)

1. **Header**: Shows "ConsultEase Faculty Unit" and faculty information
2. **Status**: Displays current availability status ("PRESENT" or "UNAVAILABLE")
3. **Consultation Requests**: Shows pending student requests
4. **Connection Status**: Indicates WiFi and MQTT connection status

### Button Controls

The Faculty Desk Unit has three buttons:

1. **Acknowledge Button (A)**:
   - Press to cycle through pending consultation requests
   - Each press shows the next request in the queue

2. **Busy/Available Button (B)**:
   - Press to toggle between "Available" and "Unavailable" status
   - Status change is immediately reflected in the Central System

3. **Complete Button (C)**:
   - Press to mark the currently displayed request as completed
   - Removes the request from the queue

### BLE Presence Detection

The Faculty Desk Unit automatically detects faculty presence using Bluetooth Low Energy (BLE).

**How it works:**

1. The unit continuously scans for the faculty's BLE beacon
2. When the beacon is detected, status changes to "Available"
3. When the beacon is not detected for a specified time, status changes to "Unavailable"

**Setting up your BLE beacon:**

- Use a dedicated BLE beacon device
- Use a smartphone with a BLE beacon app
- Use another ESP32 configured as a beacon

The BLE beacon MAC address must match the one configured in the Faculty Desk Unit.

### Handling Consultation Requests

When a student submits a consultation request:

1. The request appears on the Faculty Desk Unit display
2. The unit may emit a sound or visual alert (if configured)
3. Faculty can view the request details on the display

**To handle requests:**

1. Press the Acknowledge button (A) to cycle through requests
2. Review the request details
3. When the consultation is complete, press the Complete button (C) to remove the request

## Troubleshooting

### Central System Issues

**RFID Card Not Recognized:**

1. Ensure the card is placed directly on the reader
2. Try repositioning the card
3. If problems persist, contact system administrator

**Cannot Submit Consultation Request:**

1. Check that you've selected a faculty member
2. Ensure you've entered request details
3. Verify your network connection
4. Try refreshing the page

**System Unresponsive:**

1. Wait a few moments for the system to respond
2. If no response, try logging out and back in
3. If problems persist, contact system administrator

### Faculty Desk Unit Issues

**Display Shows "WiFi: ERR":**

1. Check WiFi credentials in the configuration
2. Ensure the WiFi network is operational
3. Restart the Faculty Desk Unit

**Display Shows "MQTT: ERR":**

1. Verify MQTT broker address in configuration
2. Ensure the MQTT broker is running
3. Check network connectivity

**BLE Detection Not Working:**

1. Ensure your BLE beacon is powered on
2. Verify the beacon MAC address matches the configuration
3. Keep the beacon within range of the Faculty Desk Unit

**Buttons Not Responding:**

1. Check button connections
2. Restart the Faculty Desk Unit
3. If problems persist, contact system administrator
