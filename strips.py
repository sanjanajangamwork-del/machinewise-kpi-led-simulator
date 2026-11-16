import json
import re
from pathlib import Path

STRIPS_FILE = Path(__file__).parent / "strips.json"

ALLOWED_MODES = {"clock", "preset"}


def load_strips():
    if not STRIPS_FILE.exists():
        return {}

    with open(STRIPS_FILE, "r") as file:
        return json.load(file)


def save_strip(strip_id, led_count, mode):
    strip_id = strip_id.strip().lower()

    if not re.fullmatch(r"strip[1-9]\d*", strip_id):
        raise ValueError("Strip ID must be strip1 or higher")

    if not isinstance(led_count, int) or led_count <= 0:
        raise ValueError("LED count must be a positive number")

    if mode not in ALLOWED_MODES:
        raise ValueError("Invalid strip mode")

    strips = load_strips()

    strips[strip_id] = {
        "led_count": led_count,
        "mode": mode,
        "topic": f"machinewise/led/{strip_id}"
    }

    with open(STRIPS_FILE, "w") as file:
        json.dump(strips, file, indent=4)


def get_strip(strip_id):
    return load_strips().get(strip_id.lower())
