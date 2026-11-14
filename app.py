from flask import Flask, request, jsonify, render_template

from strips import load_strips, save_strip, get_strip
from presets import load_presets, save_preset, get_preset, apply_preset

app = Flask(__name__)


# HOME

@app.route("/")
def home():
    return render_template("index.html")


# PRESET MANAGEMENT

@app.route("/presets", methods=["GET"])
def list_presets():
    return jsonify(load_presets())


@app.route("/presets", methods=["POST"])
def create_preset():
    data = request.get_json()

    try:
        save_preset(data["name"], data["colors"])
        return jsonify({
            "message": "Preset saved successfully"
        }), 201

    except (ValueError, KeyError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


@app.route("/presets/<name>", methods=["GET"])
def view_preset(name):
    preset = get_preset(name)

    if preset is None:
        return jsonify({"error": "Preset not found"}), 404

    return jsonify(preset)


# APPLY PRESET

@app.route("/presets/<name>/apply", methods=["POST"])
def apply_preset_api(name):
    data = request.get_json() or {}
    strip_id = data.get("strip")

    if not strip_id:
        return jsonify({"error": "Strip is required"}), 400

    strip_id = strip_id.strip().lower()

    strip = get_strip(strip_id)

    if strip is None:
        return jsonify({"error": "Strip not registered"}), 404

    if strip["mode"] != "preset":
        return jsonify({
            "error": "Selected strip is not configured for presets"
        }), 400

    try:
        result = apply_preset(name, strip_id)

        return jsonify({
            "message": "Preset published successfully!",
            "strip": strip_id,
            "topic": result["topic"],
            "led_data": result["led_data"]
        })

    except (ValueError, RuntimeError, TimeoutError, OSError) as error:
        return jsonify({"error": str(error)}), 500

# STRIP MANAGEMENT

@app.route("/strips", methods=["GET"])
def list_strips():
    return jsonify(load_strips())


@app.route("/strips", methods=["POST"])
def register_strip():
    data = request.get_json() or {}

    try:
        save_strip(
            data["strip_id"],
            data["led_count"],
            data["mode"]
        )

        return jsonify({
            "message": "Strip registered successfully"
        }), 201

    except (ValueError, KeyError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


@app.route("/strips/<strip_id>", methods=["GET"])
def view_strip(strip_id):
    strip = get_strip(strip_id)

    if strip is None:
        return jsonify({"error": "Strip not found"}), 404

    return jsonify(strip)


# RUN APPLICATION

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )