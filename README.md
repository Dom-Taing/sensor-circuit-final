# Sensor Circuit Final Project

A GitHub repository for **TECHIN 512 Final Project** - Music Rhythm Game

## 🎮 Game Description

This is an interactive **music rhythm game** with the following features:

- **4-lane gameplay** with notes falling down from the top
- **Two note types:**
  - **Filled notes**: Press the corresponding button when they reach the hit line
  - **Hollow notes**: Flick the device upward when they reach the hit line
- **Timing-based gameplay**: Hit notes precisely when they reach the hit line
- **Difficulty levels**: Different difficulties change note size, affecting hit precision requirements

## 🔧 Hardware Components

- **ESP32C3** - Main microcontroller
- **4 Buttons** - Input for filled notes
- **Accelerometer** - Motion detection for hollow notes
- **DFPlayer Mini** - Audio playback module
- **Neopixel LED Strip** (5 LEDs) - Visual feedback
- **Speaker** - Audio output
- **OLED Display** - Game interface
- **Rotary Encoder** - Menu navigation/settings
- **Miniboost** - Power management
- **LIPO Battery** - Portable power source

## 📦 Enclosure Design

The custom enclosure features a **laser-cut design** with the following specifications:

- **Materials**: Wood and acrylic construction
- **Top Layer**: Clear acrylic for LED visibility through the Neopixel strip
- **Button Layout**: Dedicated area with 4 mechanical keyboard switches
- **Key Caps**: Custom 3D printed key caps for tactile feedback
- **Assembly**: Components secured between two press-fit wood layers for stable construction

## 🗂️ Project Structure

```
sensor-circuit-final/
├── Documentation/
│   ├── Block_diagram.drawio
│   ├── circuit_diagram.kicad_sch
│   └── Readme.md
├── src/
│   ├── accelerometer.py
│   ├── code.py
│   ├── GameManager.py
│   ├── neo_pixel.py
│   ├── visual.py
│   └── Readme.md
└── README.md
``` 
