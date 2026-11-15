import os
import json
import time
import socketio
import paho.mqtt.client as mqtt

from pathlib import Path
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = "https://dev.machinewiseapp.in"
CONFIG_FILE = Path(__file__).parent / "machine_config.json"

INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", 30))
CONFIG_CHECK_SECONDS = 2

MQTT_BROKER = "machinewiseapp.in"
MQTT_PORT = 1883
MQTT_TOPIC = "machinewise/led/strip1/push"

ENABLE_LED_PUBLISH = True

sio = socketio.Client()
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

KPI_CHANNEL_ID = None
KPI_CHANNEL = None

status_updates = []
window_start = time.time()


# CONFIGURATION

def load_channel_id():
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)

        channel_id = config.get("machine_kpi_channel_id", "")

        if isinstance(channel_id, str) and channel_id.strip():
            return channel_id.strip()

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    return os.getenv("MACHINE_KPI_CHANNEL_ID", "").strip()


# MACHINE STATUS

def get_machine_status(data):
    if not isinstance(data, dict):
        return "OTHERS"

    production_status = data.get("productionStatus")

    if not data.get("online") or production_status == 898989:
        return "OFFLINE"
    elif production_status == 1:
        return "PRODUCTIVE"
    elif production_status == 0:
        return "IDLE"
    elif production_status == 2:
        return "EMERGENCY"
    else:
        return "OTHERS"


def get_led_code(status):
    mapping = {
        "PRODUCTIVE": "G",
        "IDLE": "Y",
        "OFFLINE": "R",
        "EMERGENCY": "B",
        "OTHERS": "A"
    }

    return mapping.get(status, "A")


def create_led_message(status):
    return get_led_code(status)


def calculate_currentStatus():
    if not status_updates:
        return None

    counts = Counter(status_updates)
    highest_count = max(counts.values())

    tied_statuses = {
        status for status, count in counts.items()
        if count == highest_count
    }

    return next(
        status for status in reversed(status_updates)
        if status in tied_statuses
    )


# MQTT

def on_mqtt_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT Connected Successfully!")
    else:
        print("MQTT connection failed:", reason_code)


# MACHINEWISE CONNECTION

def receive_kpi(data):
    status = get_machine_status(data)
    status_updates.append(status)


def connect_machinewise(channel_id):
    global KPI_CHANNEL_ID, KPI_CHANNEL

    if sio.connected:
        sio.disconnect()

    KPI_CHANNEL_ID = channel_id
    KPI_CHANNEL = f"kpi/{channel_id}"

    print("Connecting to MachineWise...")
    print("KPI Channel:", KPI_CHANNEL)

    sio.connect(
        SERVER_URL,
        socketio_path="/socket.io",
        transports=["websocket"]
    )

    sio.on(KPI_CHANNEL, handler=receive_kpi)

    sio.emit("subscribe", KPI_CHANNEL)

    print("Subscribed to:", KPI_CHANNEL)


def disconnect_machinewise():
    if sio.connected:
        sio.disconnect()


# MAIN

def main():
    global window_start

    print(f"Collection interval: {INTERVAL_SECONDS} seconds")

    mqtt_client.on_connect = on_mqtt_connect

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()

        timeout = time.time() + 10

        while not mqtt_client.is_connected() and time.time() < timeout:
            time.sleep(0.1)

        if not mqtt_client.is_connected():
            raise ConnectionError("Could not connect to MQTT broker")

        current_channel = load_channel_id()

        if not current_channel:
            raise ValueError("Machine KPI Channel ID is not configured")

        connect_machinewise(current_channel)

        window_start = time.time()
        last_config_check = time.time()

        while True:
            time.sleep(0.5)

            # CHECK FOR CHANNEL CHANGES

            if time.time() - last_config_check >= CONFIG_CHECK_SECONDS:
                new_channel = load_channel_id()

                if new_channel and new_channel != KPI_CHANNEL_ID:
                    print("\nKPI Channel ID changed!")
                    status_updates.clear()
                    connect_machinewise(new_channel)
                    window_start = time.time()

                last_config_check = time.time()

            # COLLECT MACHINE STATUS

            if time.time() - window_start >= INTERVAL_SECONDS:
                current_status = calculate_currentStatus()

                if current_status:
                    led_message = create_led_message(current_status)

                    print(f"Machine Status: {current_status}")
                    print(f"Generated LED Command: {led_message}")

                    if ENABLE_LED_PUBLISH:
                        result = mqtt_client.publish(
                            MQTT_TOPIC,
                            led_message,
                            qos=1,
                            retain=False
                        )

                        if result.rc == mqtt.MQTT_ERR_SUCCESS:
                            print("LED command published successfully!")
                        else:
                            print("LED command publishing failed!")
                    else:
                        print("Dry-run mode: LED command not published.")

                else:
                    print("No status updates received in this interval.")

                status_updates.clear()
                window_start = time.time()

    except KeyboardInterrupt:
        print("\nStopping program.")

    except Exception as error:
        print("Error:", error)

    finally:
        disconnect_machinewise()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


if __name__ == "__main__":
    main()