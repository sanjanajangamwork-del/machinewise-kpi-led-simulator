import os
import time
import socketio
import paho.mqtt.client as mqtt
from collections import Counter
from dotenv import load_dotenv

load_dotenv()


# ---------------- CONFIGURATION ----------------

SERVER_URL = "https://dev.machinewiseapp.in"

MACHINES = {
    "machine1": {
        "machine_id": os.getenv("MACHINE_KPI_CHANNEL_ID"),
        "strip": "strip1"
    },
    "machine2": {
        "machine_id": "68c6d5cdf99a894b7b38d35a",
        "strip": "strip2"
    }
}

INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", 30))

MQTT_BROKER = "machinewiseapp.in"
MQTT_PORT = 1883

ENABLE_LED_PUBLISH = False


# ---------------- MACHINE STATUS STORAGE ----------------

machine_status_updates = {
    config["machine_id"]: []
    for config in MACHINES.values()
    if config["machine_id"]
}


# ---------------- CLIENT INITIALIZATION ----------------

sio = socketio.Client()
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

window_start = time.time()


# ---------------- MACHINE STATUS ----------------

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


# ---------------- LED MAPPING ----------------

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


# ---------------- STATUS CALCULATION ----------------

def calculate_currentStatus(updates):

    if not updates:
        return None

    counts = Counter(updates)
    highest_count = max(counts.values())

    tied_statuses = {
        status for status, count in counts.items()
        if count == highest_count
    }

    currentStatus = next(
        status for status in reversed(updates)
        if status in tied_statuses
    )

    return currentStatus


# ---------------- MQTT CONNECTION ----------------

def on_mqtt_connect(client, userdata, flags, reason_code, properties):

    if reason_code == 0:
        print("MQTT Connected Successfully!")

    else:
        print("MQTT connection failed:", reason_code)


# ---------------- SOCKET.IO EVENTS ----------------

@sio.event
def connect():

    print("Connected to MachineWise")

    for config in MACHINES.values():

        machine_id = config["machine_id"]

        if machine_id:
            channel = f"kpi/{machine_id}"

            print("Subscribing to:", channel)

            sio.emit("subscribe", channel)


@sio.event
def connect_error(error):
    print("Connection error:", error)


@sio.event
def disconnect():
    print("Disconnected from MachineWise")


# ---------------- RECEIVE KPI DATA ----------------

@sio.on("*")
def receive_kpi(event, data):

    print("\n--- KPI EVENT RECEIVED ---")
    print("EVENT:", event)

    machine_id = (
        data.get("machineId")
        if isinstance(data, dict)
        else None
    )

    print("MACHINE ID:", machine_id)

    if machine_id not in machine_status_updates:
        print("Machine not found in configuration!")
        return

    status = get_machine_status(data)

    machine_status_updates[machine_id].append(status)

    print("STATUS ADDED:", status)


# ---------------- MAIN PROGRAM ----------------

def main():

    global window_start

    print(f"Collection interval: {INTERVAL_SECONDS} seconds")

    if not machine_status_updates:
        raise ValueError(
            "No machine configured. Check MACHINE_KPI_CHANNEL_ID in .env"
        )

    for config in MACHINES.values():

        if not config["machine_id"]:
            raise ValueError(
                "A machine ID is missing. Check your .env configuration."
            )

    mqtt_client.on_connect = on_mqtt_connect

    try:

        # Connect to MQTT

        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

        mqtt_client.loop_start()

        timeout = time.time() + 10

        while not mqtt_client.is_connected() and time.time() < timeout:
            time.sleep(0.1)

        if not mqtt_client.is_connected():
            raise ConnectionError("Could not connect to MQTT broker")

        # Connect to MachineWise

        sio.connect(
            SERVER_URL,
            socketio_path="/socket.io",
            transports=["websocket"]
        )

        window_start = time.time()

        # Continuous collection and processing

        while True:

            time.sleep(0.5)

            if time.time() - window_start >= INTERVAL_SECONDS:

                for config in MACHINES.values():

                    machine_id = config["machine_id"]
                    strip = config["strip"]

                    updates = machine_status_updates[machine_id]

                    currentStatus = calculate_currentStatus(updates)

                    if currentStatus:

                        led_message = create_led_message(currentStatus)

                        mqtt_topic = f"machinewise/led/{strip}/push"

                        print(f"\nMachine ID: {machine_id}")
                        print(f"LED Strip: {strip}")
                        print(f"Machine Status: {currentStatus}")
                        print(f"Generated LED Command: {led_message}")
                        print(f"MQTT Topic: {mqtt_topic}")

                        if ENABLE_LED_PUBLISH:

                            result = mqtt_client.publish(
                                mqtt_topic,
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
                        print(f"No status updates for {machine_id}.")

                    # Clear updates for the next interval

                    updates.clear()

                window_start = time.time()

    except KeyboardInterrupt:

        print("\nStopping program.")

    except Exception as error:

        print("Error:", error)

    finally:

        if sio.connected:
            sio.disconnect()

        mqtt_client.loop_stop()
        mqtt_client.disconnect()


if __name__ == "__main__":
    main()