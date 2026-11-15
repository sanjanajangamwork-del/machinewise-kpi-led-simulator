import paho.mqtt.client as mqtt
import json
from pathlib import Path

PRESETS_FILE = Path(__file__).parent / "presets.json"

ALLOWED_COLORS = {"R", "G", "B", "Y", "A", "O", "V", "P", "C", "W", "K"}
MQTT_BROKER = "machinewiseapp.in"
MQTT_PORT = 1883
def load_presets():
    if not PRESETS_FILE.exists():
        return {}

    with open(PRESETS_FILE, "r") as file:
        return json.load(file)


def save_preset(name, colors):
    if not name.strip():
        raise ValueError("Preset name cannot be empty")

    if not colors:
        raise ValueError("Preset must contain at least one LED")

    if not all(color in ALLOWED_COLORS for color in colors):
        raise ValueError("Invalid LED color")

    presets = load_presets()

    presets[name] = {
        "led_count": len(colors),
        "colors": colors
    }

    with open(PRESETS_FILE, "w") as file:
        json.dump(presets, file, indent=4)


def get_preset(name):
    presets = load_presets()
    return presets.get(name)

def apply_preset(name, strip):
    preset = get_preset(name)

    if preset is None:
        raise ValueError("Preset not found")

    colors = preset["colors"]
    message = "{" + ",".join(colors) + "}"
    topic = f"machinewise/led/{strip}/set"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        result = client.publish(
            topic,
            message,
            qos=1,
            retain=True
        )

        result.wait_for_publish(timeout=10)

        if not result.is_published():
            raise TimeoutError("MQTT publish timed out")

        return {
            "topic": topic,
            "led_data": message
        }

    finally:
        client.loop_stop()
        client.disconnect()