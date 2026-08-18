import os

REMINDER_BOT_TOKEN = os.environ.get("REMINDER_BOT_TOKEN")
SELFBOT_TOKEN      = os.environ.get("SELFBOT_TOKEN")

BUMP_CHANNEL_ID = int(os.environ.get("BUMP_CHANNEL_ID", ""))
BUMP_ROLE_ID    = int(os.environ.get("BUMP_ROLE_ID",    ""))

# time in seconds after last bump when reminder fires
REMINDER_OFFSET = 2.25 * 3600   # 2 hrs 15 min

# rotating bump intervals (anti-detection)
CYCLE_INTERVALS = [
    2.5  * 3600,   # cycle 0 → 2 hrs 30 min
    3.0  * 3600,   # cycle 1 → 3 hrs 00 min
    4.25 * 3600,   # cycle 2 → 4 hrs 15 min
]

DISBOARD_APP_ID = ""
STATE_FILE      = "state.json"
