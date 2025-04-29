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
   - Copy `config.env.example` to `config.env`
   - Edit `config.env` with your Firebase credentials and MQTT settings
   - **Important:** For Raspberry Pi OS Bookworm (Wayland default), set `KEYBOARD_TYPE=squeekboard` in `config.env`.
   - Configure other settings as needed (e.g., `TOUCHSCREEN_ENABLED`).

6. **Run the application:**
   ```bash
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
- Support for both Squeekboard (recommended for Wayland/Bookworm) and Onboard virtual keyboards
- Configurable keyboard settings in `config.env`

To enable on-screen keyboard:

1. Ensure the system dependencies (including `squeekboard` or `onboard`) were installed during setup (see Prerequisites).

2. Configure keyboard settings in `config.env`:
   ```ini
   TOUCHSCREEN_ENABLED=True
   KEYBOARD_ENABLED=True
   KEYBOARD_TYPE=squeekboard  # Recommended for Bookworm/Wayland
   KEYBOARD_AUTO_POPUP=True
   ```

3. **On-screen Keyboard Not Appearing**:\n   - Check `KEYBOARD_ENABLED` is set to `True` in `config.env`\n   - Verify the selected keyboard (`squeekboard` recommended) is installed via `apt`\n   - For Squeekboard issues, check D-Bus is functioning correctly\n\n4. **RFID Reader Issues:**\n   - Ensure the user running the application is in the `input` group (see Installation steps).\n   - Verify the reader is detected by the system (`lsusb`, check `/dev/input/`).\n   - If using `evdev`, ensure the reader appears as a keyboard-like device. The application might need `sudo` if permissions are incorrect, but the `input` group is preferred.\n\n## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt6 team for the GUI framework
- Eclipse Paho for the MQTT client
- Firebase team for the database solution
- All contributors to the project
