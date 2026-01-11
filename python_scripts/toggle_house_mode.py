NOTHING_MODE_NAME = "nothing"

VALID_MODE_NAMES = [
    "away",
    "sleep",
    "bedtime"
]

# `data` is available as builtin and is a dictionary with the input data.
mode = data.get("mode", NOTHING_MODE_NAME)

# `logger` and `time` are available as builtin without the need of explicit import.
if mode == NOTHING_MODE_NAME:
    logger.info("No house mode change requested.")
elif mode not in VALID_MODE_NAMES:
    logger.error("Invalid mode name: '%s'.", mode)
else:
    logger.info("Toggling house mode to '%s'.", mode)
    for name in VALID_MODE_NAMES
        if mode == name:
            hass.services.call("input_boolean", "turn_on", { "entity_id": f"input_boolean.house_mode_{name}" }, False)
        else:
            hass.services.call("input_boolean", "turn_off", { "entity_id": f"input_boolean.house_mode_{name}" }, False)

