# ConsultEase - Faculty Consultation Management System

ConsultEase is a comprehensive faculty consultation management system designed to streamline and enhance the consultation process between students and faculty members in educational institutions. The system consists of a central management application running on a Raspberry Pi with a touchscreen interface and distributed faculty desk units based on ESP32 microcontrollers.

## System Overview

### Central System
- **Platform**: Raspberry Pi 4 with touchscreen
- **OS**: Raspberry Pi OS (64-bit) with desktop
- **Interface**: PyQt6-based touchscreen UI with on-screen keyboard support
- **Database**: Firebase Realtime Database
- **Communication**: MQTT for real-time updates

### Faculty Desk Units
- **Hardware**: ESP32 development boards
- **Peripherals**: OLED displays, tactile buttons, and BLE beacons
- **Communication**: WiFi + MQTT

## Features

- **Real-time Faculty Status Tracking**: Monitor faculty availability status in real-time
- **Student Consultation Requests**: Students can request consultations through RFID authentication
- **Faculty Management**: Add, edit, and manage faculty profiles and departments
- **Office Location Management**: Map faculty to physical office locations
- **Touchscreen Support**: Optimized for touchscreen interaction with on-screen keyboard
- **Admin Dashboard**: Comprehensive system management interface
- **BLE Proximity Detection**: Automatic faculty presence detection using BLE beacons

## Installation

### Prerequisites
- Raspberry Pi 4 (4GB+ RAM recommended) with Raspberry Pi OS
- Python 3.9+ installed
- MQTT Broker (Mosquitto recommended)
- Firebase account with Realtime Database
- ESP32 with Arduino IDE for faculty desk units

### Central System Setup

1. Clone the repository:
   ```
git clone https://github.com/yourusername/consultease.git
cd consultease
```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the system:
   - Copy `config.env.example` to `config.env`
   - Edit `config.env` with your Firebase credentials and MQTT settings
   - Configure on-screen keyboard settings if using touchscreen

4. Run the application:
   ```
   python central_system/main.py
```

### Automatic Startup (Optional)

To configure the system to start automatically on boot:

1. Create a systemd service file:
   ```
   sudo nano /etc/systemd/system/consultease.service
   ```

2. Add the following content (adjust paths as necessary):
   ```
   [Unit]
   Description=ConsultEase Faculty Consultation System
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /path/to/consultease/central_system/main.py
   WorkingDirectory=/path/to/consultease
   StandardOutput=inherit
   StandardError=inherit
   Restart=always
   User=pi

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```
   sudo systemctl enable consultease.service
   sudo systemctl start consultease.service
   ```

## Touchscreen Support

ConsultEase is optimized for touchscreen interaction with the following features:

- Large, touch-friendly UI elements and controls
- On-screen keyboard support with automatic popup/hide behavior
- Support for both Squeekboard and Onboard virtual keyboards
- Configurable keyboard settings in `config.env`

To enable on-screen keyboard:

1. Ensure the following packages are installed:
   ```
   # For Squeekboard
   sudo apt install squeekboard

   # For Onboard (alternative)
   sudo apt install onboard
   ```

2. Configure keyboard settings in `config.env`:
   ```
   KEYBOARD_ENABLED=True
   KEYBOARD_TYPE=squeekboard  # or 'onboard'
   KEYBOARD_AUTO_POPUP=True
   ```

## Faculty Desk Unit Setup

1. Open `faculty_desk_unit/faculty_desk_unit.ino` in Arduino IDE
2. Install required libraries via Arduino Library Manager:
   - PubSubClient
   - Adafruit SSD1306
   - Adafruit GFX
   - ArduinoJson
3. Configure WiFi and MQTT settings in `credentials.h`
4. Flash to ESP32 device

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   - Verify Firebase credentials in `config.env`
   - Check network connectivity
   - Ensure Firebase rules allow read/write access

2. **MQTT Connection Issues**:
   - Verify MQTT broker address and credentials
   - Check if MQTT broker is running and accessible
   - Ensure proper topic permissions

3. **On-screen Keyboard Not Appearing**:
   - Check `KEYBOARD_ENABLED` is set to `True` in `config.env`
   - Verify the selected keyboard (Squeekboard/Onboard) is installed
   - For Squeekboard issues, check D-Bus is functioning correctly

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt6 team for the GUI framework
- Eclipse Paho for the MQTT client
- Firebase team for the database solution
- All contributors to the project
