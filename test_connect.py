import os
import time
import socketio
import paho.mqtt.client as mqtt
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = "https://dev.machinewiseapp.in"
KPI_CHANNEL_ID = os.getenv("MACHINE_KPI_CHANNEL_ID")
KPI_CHANNEL = f"kpi/{KPI_CHANNEL_ID}"
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", 30))

MQTT_BROKER = "machinewiseapp.in"
MQTT_PORT = 1883
MQTT_TOPIC = "machinewise/led/strip1/push"

ENABLE_LED_PUBLISH = True

sio = socketio.Client()
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

status_updates = []
window_start = time.time()   


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

    currentStatus = next(
        status for status in reversed(status_updates)
        if status in tied_statuses
    )

    return currentStatus


def on_mqtt_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT Connected Successfully!")
    else:
        print("MQTT connection failed:", reason_code)


@sio.event
def connect():
    print("Connected to MachineWise")
    print("Subscribing to:", KPI_CHANNEL)
    sio.emit("subscribe", KPI_CHANNEL)


@sio.event
def connect_error(error):
    print("Connection error:", error)


@sio.event
def disconnect():
    print("Disconnected from MachineWise")


@sio.on("*")
@sio.on(KPI_CHANNEL)
def receive_kpi(data):
    status = get_machine_status(data)
    status_updates.append(status)


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

        sio.connect(
            SERVER_URL,
            socketio_path="/socket.io",
            transports=["websocket"]
        )

        window_start = time.time()

        while True:
            time.sleep(0.5)

            if time.time() - window_start >= INTERVAL_SECONDS:
                currentStatus = calculate_currentStatus()

                if currentStatus:
                    led_message = create_led_message(currentStatus)

                    print(f"Machine Status: {currentStatus}")
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
        if sio.connected:
            sio.disconnect()

        mqtt_client.loop_stop()
        mqtt_client.disconnect()


if __name__ == "__main__":
    main()