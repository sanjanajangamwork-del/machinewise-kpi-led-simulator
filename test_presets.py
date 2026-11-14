from presets import get_preset

name = "Red Green Pattern"
strip = "strip2"

preset = get_preset(name)

if preset:
    message = "{" + ",".join(preset["colors"]) + "}"
    topic = f"machinewise/led/{strip}/set"

    print("Topic:", topic)
    print("Message:", message)
else:
    print("Preset not found")