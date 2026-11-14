# MachineWise KPI LED Simulator

A Python-based LED strip control system that integrates real-time machine status data with configurable LED patterns through MQTT.

The system provides a web dashboard to manage LED strips, create colour presets, and publish commands to individual strips.

## Overview

The project connects to the MachineWise platform to receive real-time machine KPI updates, determines machine operating conditions, and publishes corresponding LED commands through MQTT.

It also provides a web-based interface for configuring multiple LED strips and applying predefined LED colour sequences.

The application is designed for industrial status visualization and exhibition displays.

## Features

- Real-time machine KPI integration through Socket.IO.
- Machine status detection and LED colour mapping.
- MQTT-based LED command publishing.
- Configurable data collection interval.
- Support for multiple LED strips.
- Separate MQTT topics for individual strips.
- Web dashboard for LED strip management.
- Create and save reusable LED colour presets.
- Register LED strips with configurable LED counts and operating modes.
- Apply saved presets to selected LED strips.
- Docker Compose deployment for the web dashboard and live listener.

## Machine Status Mapping

| Machine Status | LED Colour |
|---|---|
| Productive | Green (G) |
| Offline | Red (R) |
| Idle | Yellow (Y) |
| Emergency | Blue (B) |
| Others | Amber (A) |

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- MQTT
- Paho MQTT Client
- Socket.IO
- Docker
- Docker Compose

## Project Structure

```text
machinewise-kpi-led-simulator/
│
├── app.py
├── test_connect.py
├── mqtt_test.py
├── test_led.py
├── test_presets.py
│
├── presets.py
├── strips.py
├── presets.json
├── strips.json
│
├── templates/
│   └── index.html
│
├── static/
│   ├── app.js
│   └── style.css
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sanjanajangamwork-del/machinewise-kpi-led-simulator.git
```

### 2. Navigate to the project directory

```bash
cd machinewise-kpi-led-simulator
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows:

```powershell
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

## Configuration

The application uses environment variables for connection and application configuration.

Create a `.env` file in the project root directory and configure the required values used by the application.

Do not upload credentials, passwords, API keys, or private connection details to GitHub.

## Running with Docker Compose

Docker Compose runs the web dashboard and live machine-data listener as separate services.

### Prerequisites

- Docker Desktop installed and running.
- A valid `.env` configuration file.
- Required MachineWise and MQTT connection details.

### 1. Build and start the application

```bash
docker compose up --build -d
```

### 2. Check running services

```bash
docker compose ps
```

The application runs two services:

| Service | Purpose |
|---|---|
| `web` | Runs the Flask dashboard |
| `live-listener` | Receives MachineWise KPI data and processes LED status updates |

### 3. Access the dashboard

Open the following address in your browser:

```text
http://localhost:5000
```

### 4. View application logs

Web dashboard:

```bash
docker compose logs -f web
```

Live machine-data listener:

```bash
docker compose logs -f live-listener
```

### 5. Stop the application

```bash
docker compose down
```

## Dashboard Operations

The web dashboard provides three main sections.

### 1. Preset Manager

- Enter a preset name.
- Define an LED colour sequence using comma-separated colour codes.
- Save the preset for future use.

Example:

```text
R,R,R,G,G,G,G
```

### 2. Strip Configuration

- Enter a unique strip ID.
- Specify the number of LEDs.
- Select the operating mode.
- Register the strip.

Supported modes:

| Mode | Description |
|---|---|
| Clock | Live machine-data LED operation |
| Preset | Configurable LED colour patterns |

### 3. Strip Controller

- Select a registered LED strip.
- Select a saved preset.
- Apply the preset.

The application publishes the corresponding LED sequence to the selected strip's MQTT topic.

## MQTT Topic Structure

Each LED strip uses its own MQTT topic namespace.

Base topic:

```text
machinewise/led/<strip_id>
```

Examples:

**Strip 1 – Live machine status**

```text
machinewise/led/strip1/push
```

**Strip 2 – Preset configuration**

```text
machinewise/led/strip2/set
```

**Strip 3 – Preset configuration**

```text
machinewise/led/strip3/set
```

### LED Command Formats

Live status commands use individual colour codes.

Example:

```text
G
```

Preset commands use a complete LED sequence.

Example:

```text
{R,R,G,G,Y,A}
```

## Working Flow

### Live Machine Status

1. Connect to the MachineWise platform.
2. Receive machine KPI updates through Socket.IO.
3. Process production and machine-condition information.
4. Determine the current machine status.
5. Map the status to its corresponding LED colour.
6. Publish the LED command through MQTT.
7. Reflect the machine condition through the LED strip.

### Preset Configuration

1. Create a colour sequence through the dashboard.
2. Save the preset.
3. Register an LED strip.
4. Select the target strip and saved preset.
5. Apply the preset.
6. Publish the LED sequence to the corresponding MQTT topic.

## Data Persistence

Saved presets and registered LED strip configurations are maintained in:

- `presets.json`
- `strips.json`

Docker Compose mounts these files so that application data persists across container restarts.

## Development and Testing

The project includes scripts for connection testing, LED command testing, MQTT testing, and preset testing.

Examples:

```bash
python test_connect.py
```

```bash
python mqtt_test.py
```

Use these scripts when testing the corresponding application components independently.

## Docker Files

| File | Purpose |
|---|---|
| `Dockerfile` | Defines the Python application environment and dependencies |
| `docker-compose.yml` | Configures and runs the application services |
| `.dockerignore` | Excludes unnecessary files from the Docker build context |
| `.gitignore` | Prevents local and sensitive files from being committed |

## Future Hardware Integration

The system supports MQTT-based communication with configurable LED strips.

Physical LED operation depends on the corresponding ESP32 firmware, hardware configuration, and MQTT connectivity.