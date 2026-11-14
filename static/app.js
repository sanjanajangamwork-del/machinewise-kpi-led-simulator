const $ = (id) => document.getElementById(id);


// NOTIFICATIONS

function notice(message, type = "success") {
    const el = $("message");

    el.textContent = message;
    el.className = `notice show ${type}`;

    setTimeout(() => {
        el.className = "notice";
    }, 3500);
}


// API REQUESTS

async function api(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        },
        ...options
    });

    let data = {};

    try {
        data = await response.json();
    } catch {}

    if (!response.ok) {
        throw new Error(
            data.error || data.message || `Request failed (${response.status})`
        );
    }

    return data;
}


// PRESET MANAGER

$("savePresetBtn").onclick = async () => {
    const name = $("presetName").value.trim();

    const input = $("presetColors").value.trim();

    if (!name || !input) {
        return notice("Enter a preset name and LED sequence.", "error");
    }

    const colors = input
        .split(",")
        .map(color => color.trim().toUpperCase());

    if (colors.some(color => !color)) {
        return notice("Invalid LED sequence. Example: R,R,G,G", "error");
    }

    try {
        const result = await api("/presets", {
            method: "POST",
            body: JSON.stringify({ name, colors })
        });

        notice(result.message || "Preset saved successfully.");

        $("presetName").value = "";
        $("presetColors").value = "";

        await loadPresets();

    } catch (error) {
        notice(error.message, "error");
    }
};


async function loadPresets() {
    const presets = await api("/presets");

    $("presetList").innerHTML = "";
    $("targetPreset").innerHTML =
        '<option value="">Choose a preset</option>';

    const names = Object.keys(presets);

    if (names.length === 0) {
        $("presetList").innerHTML =
            '<p class="empty">No presets saved yet.</p>';
    }

    names.forEach(name => {
        const preset = presets[name];

        const item = document.createElement("div");
        item.className = "item";

        const title = document.createElement("span");
        title.textContent = name;

        const details = document.createElement("small");
        details.textContent = `${preset.led_count} LEDs`;

        item.append(title, details);
        $("presetList").appendChild(item);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;

        $("targetPreset").appendChild(option);
    });
}


// STRIP CONFIGURATION

$("registerStripBtn").onclick = async () => {

    const body = {
        strip_id: $("stripId").value.trim(),
        led_count: Number($("stripLedCount").value),
        mode: $("stripMode").value
    };

    if (
        !body.strip_id ||
        !Number.isInteger(body.led_count) ||
        body.led_count < 1
    ) {
        return notice("Enter a valid strip ID and LED count.", "error");
    }

    try {
        const result = await api("/strips", {
            method: "POST",
            body: JSON.stringify(body)
        });

        notice(result.message || "Strip registered successfully.");

        $("stripId").value = "";
        $("stripLedCount").value = 60;

        await loadStrips();

    } catch (error) {
        notice(error.message, "error");
    }
};


async function loadStrips() {
    const strips = await api("/strips");

    $("stripList").innerHTML = "";
    $("targetStrip").innerHTML =
        '<option value="">Choose a strip</option>';

    const ids = Object.keys(strips);

    if (ids.length === 0) {
        $("stripList").innerHTML =
            '<p class="empty">No strips registered yet.</p>';
    }

    ids.forEach(id => {
        const strip = strips[id];

        const item = document.createElement("div");
        item.className = "item";

        const title = document.createElement("span");
        title.textContent = id;

        const details = document.createElement("small");
        details.textContent = `${strip.led_count} LEDs · ${strip.mode}`;

        item.append(title, details);
        $("stripList").appendChild(item);

        const option = document.createElement("option");
        option.value = id;
        option.textContent = id;

        $("targetStrip").appendChild(option);
    });
}


// APPLY PRESET

$("applyPresetBtn").onclick = async () => {

    const strip = $("targetStrip").value;
    const preset = $("targetPreset").value;

    if (!strip || !preset) {
        return notice("Select both a strip and a preset.", "error");
    }

    try {
        const result = await api(
            `/presets/${encodeURIComponent(preset)}/apply`,
            {
                method: "POST",
                body: JSON.stringify({ strip })
            }
        );

        $("applyResult").innerHTML = "";

        const heading = document.createElement("strong");
        heading.textContent = "DRY-RUN OUTPUT";

        const topic = document.createElement("code");
        topic.textContent = `Topic: ${result.topic}`;

        const frame = document.createElement("code");
        frame.textContent = `LED Sequence: ${result.led_data}`;

        const message = document.createElement("p");
        message.className = "empty";
        message.textContent = result.message;

        $("applyResult").append(heading, topic, frame, message);

        notice("Command preview generated. No MQTT message published.");

    } catch (error) {
        notice(error.message, "error");
    }
};


// INITIAL LOAD

Promise.all([
    loadPresets(),
    loadStrips()
]).catch(error => {
    notice(error.message, "error");
});