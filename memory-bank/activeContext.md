# Active Context
*Last updated: 2023-07-21*

## Current Focus
- Implementing RFID-Firebase integration for student authentication
- Developing MQTT heartbeat mechanism for ESP32 units
- Optimizing touchscreen UI for Raspberry Pi display
- Implementing BLE beacon detection and presence tracking
- Enhancing faculty department organization and display
- Preparing system for production deployment
- Integrating on-screen keyboard support for touchscreen usability

## Recent Changes
- Migrated from local SQLite database to Firebase Realtime Database
- Updated Python requirements to include Firebase Admin SDK
- Added MQTT broker configuration for real-time communication
- Implemented faculty and office management in admin interface
- Enhanced faculty UI components to display department information prominently
- Implemented structured department selection with common academic departments
- Improved faculty desk unit firmware with persistent storage and better connectivity
- Updated configuration files for production environment
- Enhanced deployment documentation with detailed setup instructions
- Added Squeekboard on-screen keyboard integration with automatic popup behavior

## Active Decisions
- Using PyQt6 instead of PyQt5 for improved touchscreen support
- Firebase security rules to enforce role-based access control
- MQTT topic structure for efficient routing of notifications
- BLE scanning parameters for optimal power/performance balance
- Standardizing department names using predefined list while allowing custom entries
- Implementing systemd service for automatic startup on boot
- Using version-pinned dependencies for predictable deployments
- Supporting both Squeekboard and Onboard virtual keyboards for different platforms

## Implementation Challenges
- RFID reader integration with PyQt event loop
- ESP32 deep sleep impacts BLE advertisement detection
- Firebase offline capabilities require careful synchronization
- Touch UI requires larger tap targets and simplified navigation
- Dbus communication with Squeekboard requires specific error handling
- Different on-screen keyboard implementations need unified interface

## Current Architecture Insights
- The faculty model is central to the system, connecting student requests with physical spaces
- MQTT provides the real-time backbone for status updates across devices
- Firebase security rules govern access patterns across user roles
- The admin interface provides comprehensive management capabilities
- The keyboard handler module detects input fields and manages keyboard visibility

## Technical Constraints
- Raspberry Pi has limited GPU acceleration for UI rendering
- ESP32 battery life considerations limit BLE scanning frequency
- MQTT QoS levels impact message delivery guarantees vs. network overhead
- Firebase query depths impact performance on resource-constrained devices
- Squeekboard requires DBus communication which is Linux-specific

## Next Steps
1. Complete Firebase authentication flow for RFID login
2. Develop faculty unit UI mockups for OLED display
3. Implement BLE scanning optimizations for ESP32
4. Create comprehensive system test plan
5. Evaluate on-screen keyboard performance with various text input widgets

// File version: 1.5-keyboard
