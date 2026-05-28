import json
import os
import time
from config import STATE_FILE

def read_state():
    if not os.path.exists(STATE_FILE):
        # first run — start cycle fresh from now
        # bot will wait full interval before first bump
        default = {
            "last_bump_time": time.time(),
            "cycle_index": 0,
            "reminder_sent": False
        }
        write_state(default)
        return default
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def write_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
