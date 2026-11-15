const $ = (id) => document.getElementById(id);

function notice(message, type = "success") {
    const el = $("message");
    el.textContent = message;
    el.className = `notice show ${type}`;
    setTimeout(() => { el.className = "notice"; }, 3500);
}

async function api(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        },
        ...options
    });

    let data = {};
    try { data = await response.json(); } catch {}

    if (!response.ok) {
        throw new Error(data.error || data.message || `Request failed (${response.status})`);
    }
    return data;
}

// PRESETS
$("savePresetBtn").onclick = async () => {
    const name = $("presetName").value.trim();
    const input = $("presetColors").value.trim();

    if (!name || !input) {
        return notice("Enter a preset name and LED sequence.", "error");
    }

    const colors = input.split(",").map(color => color.trim().toUpperCase());
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
    const selectors = [$("targetPreset"), $("managePreset")];

    selectors.forEach(select => {
        const previous = select.value;
        select.innerHTML = '<option value="">Choose a preset</option>';

        Object.keys(presets).forEach(name => {
            const option = document.createElement("option");
            option.value = name;
            option.textContent = name;
            select.appendChild(option);
        });

        if (presets[previous]) select.value = previous;
    });
}

// STRIPS
$("registerStripBtn").onclick = async () => {
    const body = {
        strip_id: $("stripId").value.trim(),
        led_count: Number($("stripLedCount").value),
        mode: $("stripMode").value
    };

    if (!body.strip_id || !Number.isInteger(body.led_count) || body.led_count < 1) {
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
    const select = $("targetStrip");
    const previous = select.value;
    select.innerHTML = '<option value="">Choose a strip</option>';

    Object.keys(strips).forEach(id => {
        const option = document.createElement("option");
        option.value = id;
        option.textContent = id;
        select.appendChild(option);
    });

    if (strips[previous]) select.value = previous;
    updateApplyButton();
}

// APPLY PRESET
function updateApplyButton() {
    $("applyPresetBtn").disabled = !($("targetStrip").value && $("targetPreset").value);
}

$("targetStrip").addEventListener("change", updateApplyButton);
$("targetPreset").addEventListener("change", updateApplyButton);

$("applyPresetBtn").onclick = async () => {
    const strip = $("targetStrip").value;
    const preset = $("targetPreset").value;

    if (!strip || !preset) {
        return notice("Select both a strip and a preset.", "error");
    }

    try {
        const result = await api(`/presets/${encodeURIComponent(preset)}/apply`, {
            method: "POST",
            body: JSON.stringify({ strip })
        });
        notice(result.message || "Preset applied and MQTT command published.");
    } catch (error) {
        notice(error.message, "error");
    }
};

// MACHINE CONFIGURATION
async function loadMachineConfig() {
    try {
        const config = await api("/machine-config");
        $("machineChannelId").value = config.machine_kpi_channel_id || "";
    } catch (error) {
        notice(error.message, "error");
    }
}

$("saveMachineConfigBtn").onclick = async () => {
    const channelId = $("machineChannelId").value.trim();
    if (!channelId) return notice("Enter a valid KPI Channel ID.", "error");

    try {
        const result = await api("/machine-config", {
            method: "POST",
            body: JSON.stringify({ machine_kpi_channel_id: channelId })
        });
        notice(result.message || "Configuration saved.");
    } catch (error) {
        notice(error.message, "error");
    }
};

// INITIAL LOAD
Promise.all([loadPresets(), loadStrips(), loadMachineConfig()])
    .catch(error => notice(error.message, "error"));
