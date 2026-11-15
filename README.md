# MachineWise KPI LED Simulator

A Python-based application that connects MachineWise machine data to MQTT-controlled LED strips for real-time industrial status visualization.

## Features

- Live machine KPI integration using Socket.IO.
- Automatic machine status detection and LED colour mapping.
- MQTT-based LED command publishing with trailing effects.
- Web dashboard for managing LED strips.
- Create, save and apply reusable LED presets.
- Configurable LED strip IDs, LED counts and operating modes.
- Docker Compose deployment.

## Technology Stack

Python · Flask · JavaScript · HTML · CSS · Socket.IO · MQTT · Docker

## Machine Status Mapping

| Machine Status | LED Colour |
|---|---|
| Productive | Green (G) |
| Idle | Yellow (Y) |
| Offline | Red (R) |
| Emergency | Blue (B) |
| Others | Amber (A) |

## Project Structure

```text
machinewise-kpi-led-simulator/
├── app.py
├── test_connect.py
├── mqtt_test.py
├── test_led.py
├── presets.py
├── strips.py
├── machine_config.json
├── presets.json
├── strips.json
├── templates/
│   └── index.html
├── static/
│   ├── app.js
│   └── style.css
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup and Execution

### Prerequisites
- Python
- Docker Desktop
- MachineWise and MQTT connection configuration

### 1. Clone the repository

```bash
git clone https://github.com/sanjanajangamwork-del/machinewise-kpi-led-simulator.git
cd machinewise-kpi-led-simulator
```

### 2. Configure environment

Create a `.env` file in the project root with the required connection settings.

Configure the MachineWise KPI channel ID in `machine_config.json`.

Do not commit credentials or private connection details.

### 3. Start using Docker Compose

```bash
docker compose up --build -d
```

### 4. Access the dashboard

Open:

```text
http://localhost:5000
```

### Useful Docker Commands

```bash
# Check services
docker compose ps

# View live listener logs
docker compose logs -f live-listener

# View dashboard logs
docker compose logs -f web

# Stop services
docker compose down
```

## System Workflow

**Live machine monitoring:**

MachineWise → Socket.IO Listener → Status Detection → MQTT → LED Strip

**Preset control:**

Dashboard → Preset Selection → MQTT → LED Strip

## MQTT Communication

The application uses separate MQTT topic namespaces for individual LED strips.

Example topics:

```text
machinewise/led/strip1/push
machinewise/led/strip2/set
```

- `/push` – Used for live LED updates and trailing effects.
- `/set` – Used for preset-based LED sequence updates.

## Data Storage

- `machine_config.json` – Machine KPI channel configuration.
- `presets.json` – Saved LED presets.
- `strips.json` – Registered LED strip configurations.

These files are mounted through Docker Compose to retain application configuration and saved data across container restarts.