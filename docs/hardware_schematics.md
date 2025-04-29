# ConsultEase Hardware Schematics

This document provides schematic diagrams and wiring instructions for the ConsultEase system hardware components.

## Central System (Raspberry Pi)

The central system uses a Raspberry Pi with a USB RFID reader. The setup is straightforward as the RFID reader connects via USB.

```
┌───────────────────────┐                  ┌───────────────────┐
│                       │                  │                   │
│    Raspberry Pi 4     │                  │   USB RFID Reader │
│                       │                  │                   │
│  ┌─────────────────┐  │                  │                   │
│  │                 │  │                  │                   │
│  │                 │  │                  │                   │
│  │                 │  │      USB         │                   │
│  │                 │◄─┼──────────────────┼───────────────────┤
│  │                 │  │   Connection     │                   │
│  │                 │  │                  │                   │
│  │                 │  │                  │                   │
│  └─────────────────┘  │                  │                   │
│                       │                  │                   │
└───────────────────────┘                  └───────────────────┘
```

### Power Supply

- Raspberry Pi: 5V/3A power supply via USB-C
- RFID Reader: Powered via USB from Raspberry Pi

### Network Connection

- Ethernet or WiFi connection to the local network
- Must be on the same network as the Faculty Desk Units

## Faculty Desk Unit (ESP32)

The faculty desk unit consists of an ESP32 development board, an SSD1306 OLED display, and three push buttons.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                       ESP32 Development Board                   │
│                                                                 │
│    ┌─────┐                                           ┌─────┐    │
│    │     │ 3.3V                                      │     │    │
│    │     ├─────────────────────────────────┐         │     │    │
│    │     │ GND                             │         │     │    │
│    │     ├────────────────────────────┐    │         │     │    │
│    │     │ GPIO21 (SDA)               │    │         │     │    │
│    │     ├───────────────────┐        │    │         │     │    │
│    │     │ GPIO22 (SCL)      │        │    │         │     │    │
│    │     ├──────────┐        │        │    │         │     │    │
│    │     │ GPIO12   │        │        │    │         │     │    │
│    │     ├────┐     │        │        │    │         │     │    │
│    │     │ G14│     │        │        │    │         │     │    │
│    │     ├─┐  │     │        │        │    │         │     │    │
│    │     │G│  │     │        │        │    │         │     │    │
│    │     │2│  │     │        │        │    │         │     │    │
│    │     │7│  │     │        │        │    │         │     │    │
│    └─────┘ │  │     │        │        │    │         └─────┘    │
│            │  │     │        │        │    │                    │
└────────────┼──┼─────┼────────┼────────┼────┼────────────────────┘
             │  │     │        │        │    │                     
             │  │     │        │        │    │                     
┌────────────┼──┼─────┼────────┼────────┼────┼────────────────────┐
│            │  │     │        │        │    │                    │
│  ┌─────────┴──┴─────┴──┐  ┌──┴────────┴────┴───────────┐       │
│  │                     │  │                            │       │
│  │   Push Buttons      │  │     SSD1306 OLED Display   │       │
│  │                     │  │                            │       │
│  │  ┌───┐ ┌───┐ ┌───┐  │  │  ┌────────────────────┐    │       │
│  │  │ A │ │ B │ │ C │  │  │  │                    │    │       │
│  │  └───┘ └───┘ └───┘  │  │  │                    │    │       │
│  │   ACK   BUSY  COMP  │  │  │                    │    │       │
│  │                     │  │  │                    │    │       │
│  └─────────────────────┘  │  └────────────────────┘    │       │
│                           │                            │       │
└───────────────────────────┴────────────────────────────┴───────┘
```

### Wiring Connections

#### SSD1306 OLED Display

| OLED Pin | ESP32 Pin | Description     |
|----------|-----------|-----------------|
| VCC      | 3.3V      | Power supply    |
| GND      | GND       | Ground          |
| SCL      | GPIO22    | Clock line      |
| SDA      | GPIO21    | Data line       |

#### Push Buttons

Each button connects between the specified GPIO pin and GND. Internal pull-up resistors are enabled in software.

| Button Function | ESP32 Pin | Connection                |
|-----------------|-----------|---------------------------|
| Acknowledge     | GPIO12    | Between GPIO12 and GND    |
| Busy/Available  | GPIO14    | Between GPIO14 and GND    |
| Complete        | GPIO27    | Between GPIO27 and GND    |

### Power Supply

- ESP32: 5V power supply via USB or external power supply
- OLED Display: 3.3V from ESP32
- Buttons: No external power needed

### BLE Beacon

The faculty's BLE beacon can be:

1. A dedicated BLE beacon device
2. A smartphone running a BLE beacon app
3. Another ESP32 configured as a BLE beacon

The ESP32 will scan for the configured BLE MAC address to determine faculty presence.

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                         WiFi Network                            │
│                                                                 │
└───────────┬─────────────────────────────────┬──────────────────┘
            │                                 │                    
            │                                 │                    
┌───────────▼─────────────┐       ┌───────────▼──────────────────┐
│                         │       │                              │
│    Raspberry Pi         │       │    ESP32 Faculty Desk Unit   │
│    Central System       │       │                              │
│                         │       │    ┌──────────────────────┐  │
│  ┌─────────────────┐    │       │    │                      │  │
│  │                 │    │       │    │   OLED Display       │  │
│  │  PyQt UI        │    │       │    │                      │  │
│  │                 │    │       │    └──────────────────────┘  │
│  └─────────────────┘    │       │                              │
│                         │       │    ┌──────────────────────┐  │
│  ┌─────────────────┐    │       │    │                      │  │
│  │                 │    │       │    │   Push Buttons       │  │
│  │  RFID Reader    │    │       │    │                      │  │
│  │                 │    │       │    └──────────────────────┘  │
│  └─────────────────┘    │       │                              │
│                         │       └──────────────────────────────┘
└─────────────────────────┘                     ▲                 
                                                │                 
                                                │                 
                                      ┌─────────▼─────────────┐   
                                      │                       │   
                                      │   BLE Beacon          │   
                                      │   (Faculty Device)    │   
                                      │                       │   
                                      └───────────────────────┘   
```

### Communication Flow

1. **RFID Authentication**:
   - Student scans RFID card at central system
   - System validates against database
   - Student is authenticated and can access dashboard

2. **Faculty Presence Detection**:
   - ESP32 scans for faculty's BLE beacon
   - When detected, status changes to "Available"
   - Status is published to MQTT broker

3. **Consultation Requests**:
   - Student submits request via central system
   - Request is published to MQTT broker
   - Faculty desk unit receives and displays request

4. **Status Updates**:
   - Faculty can manually toggle status via buttons
   - Status changes are published to MQTT broker
   - Central system updates faculty availability display

## Parts List

### Central System

- Raspberry Pi 4 (2GB+ RAM)
- MicroSD card (16GB+)
- 5V/3A USB-C power supply
- USB RFID Reader (13.56MHz)
- RFID cards/tags
- Display, keyboard, and mouse
- Case for Raspberry Pi (optional)

### Faculty Desk Unit

- ESP32 development board (e.g., ESP32-WROOM-32)
- SSD1306 OLED display (128x64 pixels)
- 3x Push buttons
- Jumper wires
- Breadboard or PCB
- 5V power supply
- BLE beacon device or smartphone
- Case (optional)

## Assembly Instructions

### Central System

1. Install Raspberry Pi OS on the microSD card
2. Insert the microSD card into the Raspberry Pi
3. Connect display, keyboard, and mouse
4. Connect the USB RFID reader
5. Power on the Raspberry Pi
6. Follow the software installation instructions in the main README

### Faculty Desk Unit

1. Connect the SSD1306 OLED display to the ESP32 following the wiring diagram
2. Connect the three push buttons to the ESP32
3. Upload the firmware using Arduino IDE
4. Power the ESP32 via USB or external power supply
5. Configure the BLE beacon with the MAC address specified in the firmware
