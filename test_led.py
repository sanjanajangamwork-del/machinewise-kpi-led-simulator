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
    return f"60{get_led_code(status)}"


for status in ["PRODUCTIVE", "IDLE", "OFFLINE", "EMERGENCY", "OTHERS"]:
    print(create_led_message(status))