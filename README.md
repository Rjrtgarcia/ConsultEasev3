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
- **Automatic RFID Reader Detection**: Smart detection of USB RFID readers without manual configuration

## Recent Updates

- **PyQt6 Compatibility Improvements**: Fixed compatibility issues with modern PyQt6 syntax:
  - Updated QFont.Bold to QFont.Weight.Bold
  - Updated QSizePolicy.Expanding to QSizePolicy.Policy.Expanding
  - Improved keyboard handler implementation
- **Automatic RFID Reader Detection**: The system now automatically detects common USB RFID readers without requiring manual configuration
  - Added support for 10+ common RFID reader models
  - Implemented device caching for faster startup
  - Added reader information display on login screen
- **Improved On-screen Keyboard Support**: Better integration with Squeekboard on Wayland systems
- **Database Connection Improvements**: Enhanced stability for both Firebase and PostgreSQL connections
- **Security Enhancements**: Improved Firebase security rules implementation

## Installation

### Prerequisites
- Raspberry Pi 4 (4GB+ RAM recommended) with Raspberry Pi OS (Bookworm 64-bit recommended)
- Python 3.9+ installed
- MQTT Broker (Mosquitto recommended)
- Firebase account with Realtime Database
- ESP32 with Arduino IDE for faculty desk units

### Central System Setup

1. **Install System Dependencies:**
   Before installing Python packages, install the required system libraries:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-dev libusb-1.0-0-dev libhidapi-dev libdbus-1-dev libdbus-glib-1-dev squeekboard qt6-base-dev qt6-base-dev-tools
   ```
   *(Note: PyQt6 might pull some Qt dependencies, but installing `qt6-base-dev` ensures build tools are present if needed)*

2. **Grant Input Device Permissions:**
   The RFID reader often acts as a keyboard. To allow the application to read it directly without typing globally, add your user to the `input` group (requires logout/login or reboot):
   ```bash
   sudo usermod -a -G input $USER 
   ```
   *(Replace `$USER` with the actual username if not running as the logged-in user, e.g., `pi`)*

3. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/consultease.git # Replace with your repo URL
   cd consultease
   ```

4. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure the system:**
   - Copy `.env.sample` to `.env` in the central_system directory
   - Edit `.env` with your Firebase credentials, MQTT settings, and other configuration options
   - **Important:** For Raspberry Pi OS Bookworm (Wayland default), set `KEYBOARD_TYPE=squeekboard` in `.env`.
   - Configure other settings as needed (e.g., `TOUCHSCREEN_ENABLED`).

6. **Run the application:**
   ```bash
   python central_system/main.py
   ```

### Environment Configuration

ConsultEase uses a `.env` file for configuration. A sample configuration file (`.env.sample`) is provided in the central_system directory. To set up your environment:

1. Copy the sample configuration:
   ```bash
   cp central_system/.env.sample central_system/.env
   ```

2. Edit the `.env` file to match your environment:
   ```
   # Application Settings
   APP_NAME=ConsultEase
   DEBUG_MODE=True/False  # Set to False in production
   TOUCHSCREEN_ENABLED=True/False
   KEYBOARD_ENABLED=True/False
   THEME=Dark  # Options: Light, Dark, High Contrast

   # Database Settings
   DB_TYPE=firebase
   DB_URL=https://your-firebase-rtdb.firebaseio.com/
   DB_API_KEY=your-api-key-here

   # MQTT Settings
   MQTT_BROKER=localhost
   MQTT_PORT=1883
   MQTT_CLIENT_ID=central_system
   MQTT_USERNAME=your-username
   MQTT_PASSWORD=your-password

   # Hardware Settings
   RFID_SIMULATION=False       # Set to True for RFID reader simulation mode
   RFID_AUTO_DETECT=True       # Automatically detect USB RFID readers
   # RFID_VENDOR_ID=FFFF       # Optional: Manual override for reader vendor ID
   # RFID_PRODUCT_ID=0035      # Optional: Manual override for reader product ID

   # Logging
   LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
   LOG_TO_FILE=True/False
   ```

3. The application automatically searches for the `.env` file in these locations (in order):
   - `central_system/.env` (recommended)
   - Project root `.env`
   - Legacy `central_system/config.env`

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
- Support for both Squeekboard (recommended for Wayland/Bookworm) and Onboard virtual keyboards
- Configurable keyboard settings in `.env`

To enable on-screen keyboard:

1. Ensure the system dependencies (including `squeekboard` or `onboard`) were installed during setup (see Prerequisites).

2. Configure keyboard settings in `.env`:
   ```ini
   TOUCHSCREEN_ENABLED=True
   KEYBOARD_ENABLED=True
   KEYBOARD_TYPE=squeekboard  # Recommended for Bookworm/Wayland
   KEYBOARD_AUTO_POPUP=True
   ```

## Troubleshooting

### Common Issues

1. **PyQt6 Compatibility Issues**:
   - If you encounter `QFont.Bold` errors, ensure you're using the updated syntax: `QFont.Weight.Bold`
   - For `QSizePolicy` errors, use the new enum syntax: `QSizePolicy.Policy.Expanding`
   - For module import errors, check that you've included all necessary imports (e.g., `QApplication`)

2. **On-screen Keyboard Issues**:
   - Check `KEYBOARD_ENABLED` is set to `True` in `.env`
   - Verify the selected keyboard (`squeekboard` recommended) is installed via `apt`
   - For Squeekboard issues on Wayland, check D-Bus is functioning correctly

3. **RFID Reader Issues**:
   - The system automatically detects common USB RFID readers. Check the login screen for detection messages.
   - If auto-detection fails, you can manually set the RFID_VENDOR_ID and RFID_PRODUCT_ID in config.env.
   - Ensure the user running the application is in the `input` group (see Installation steps).
   - Verify the reader is detected by the system (`lsusb` command on Linux, Device Manager on Windows).
   - If using `evdev`, ensure the reader appears as a keyboard-like device.
   - Run `lsusb` to get the vendor and product IDs of your reader if manual configuration is needed.

4. **Database Connection Issues**:
   - For Firebase, ensure your security rules are correctly formatted with the required `if` keyword before conditional expressions
   - Verify your service account key file is correctly placed and has proper permissions
   - See the DATABASE_SETUP_GUIDE.md for detailed database configuration instructions

5. **Default Admin Login**:
   - Username: admin
   - Password: admin123

## Documentation

- **[Database Setup Guide](DATABASE_SETUP_GUIDE.md)**: Comprehensive instructions for setting up and configuring the database
- **[Production Checklist](PRODUCTION_CHECKLIST.md)**: Requirements for production deployment
- **[User Manual](docs/user_manual.md)**: Detailed usage instructions for all user types
- **[Hardware Schematics](docs/hardware_schematics.md)**: Technical details about the hardware components

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt6 team for the GUI framework
- Eclipse Paho for the MQTT client
- Firebase team for the database solution
- All contributors to the project
