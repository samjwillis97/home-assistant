NOTHING_MODE_NAME = "nothing"

VALID_MODE_NAMES = [
    NOTHING_MODE_NAME,
    "away",
    "sleep",
    "bedtime"
]

# `data` is available as builtin and is a dictionary with the input data.
mode = data.get("mode", NOTHING_MODE_NAME)

if mode not in VALID_MODE_NAMES:
    logger.error("Invalid mode name: '%s'.", mode)
else:
# `logger` and `time` are available as builtin without the need of explicit import.
    logger.info("Toggling house mode to '%s'.", mode)


