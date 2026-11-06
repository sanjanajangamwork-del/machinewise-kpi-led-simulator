# MachineWise KPI LED Simulator

A Python-based machine status simulator that receives real-time machine KPI data through MQTT and visualizes machine conditions using LED indicators.

## Overview

The project connects to the MachineWise platform, retrieves machine KPI updates, determines the current machine status, and publishes corresponding LED color commands through MQTT.

It is designed to simulate the LED status indicators used in industrial environments and exhibition displays.

## Features

- Connects to the MachineWise platform.
- Receives machine KPI data through MQTT.
- Processes machine production status and breakdown information.
- Maps machine conditions to LED colors.
- Supports multiple machine status indicators.
- Publishes status updates through MQTT.
- Configurable data collection interval.

## Machine Status Mapping

| Machine Status | LED Color |
|---|---|
| Productive | Green |
| Offline | Red |
| Idle | Yellow |
| Emergency | Blue |
| Others | Amber |

## Technologies Used

- Python
- MQTT
- Socket.IO  
- Paho MQTT Client

## Project Structure

text
machinewise-kpi/
│
├── test_connect.py
├── mqtt_test.py
├── requirements.txt
├── README.md
├── .gitignore
└── venv/



## Installation

### 1. Clone the repository

git clone https://github.com/sanjanajangamwork-del/machinewise-kpi-led-simulator.git

### 2. Navigate to the project
cd machinewise-kpi-led-simulator

### 3. Create a virtual environment
python -m venv venv

### 4. Activate the virtual environment
Windows:
venv\Scripts\activate

### 5. Install dependencies
pip install -r requirements.txt
```

## Configuration

Configure the required connection details and credentials using environment variables or the project's configuration settings.

Do not upload credentials, API keys, passwords, or private connection details to GitHub.

## Running the Project

Run the simulator using:

python simulator.py
```

Use the appropriate connection-testing script when required:

```bash
python test_connect.py
```

## Working Flow

1. Connect to the MachineWise platform.
2. Receive machine KPI data.
3. Extract relevant production and machine-condition information.
4. Determine the machine's current status.
5. Map the status to its corresponding LED color.
6. Publish the LED update through MQTT.
7. Visualize machine conditions through the LED indicators.

 