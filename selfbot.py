import asyncio
import aiohttp
import time
import random
import string
import logging

from config import (
    SELFBOT_TOKEN, BUMP_CHANNEL_ID,
    DISBOARD_APP_ID, CYCLE_INTERVALS
)
from state_manager import read_state, write_state

logging.basicConfig(
    level=logging.INFO,
    format="[SELFBOT]  %(asctime)s %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

HEADERS = {
    "Authorization": SELFBOT_TOKEN,
    "Content-Type":  "application/json",
    "User-Agent":    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


async def get_guild_id(session: aiohttp.ClientSession) -> str:
    async with session.get(
        f"https://discord.com/api/v9/channels/{BUMP_CHANNEL_ID}",
        headers=HEADERS
    ) as resp:
        data = await resp.json()
        return data["guild_id"]


async def get_bump_command(session: aiohttp.ClientSession, guild_id: str):
    """Fetch Disboard's /bump command object from the guild."""
    async with session.get(
        f"https://discord.com/api/v9/guilds/{guild_id}/application-command-index",
        headers=HEADERS
    ) as resp:
        data = await resp.json()
        for cmd in data.get("application_commands", []):
            if (
                cmd.get("name") == "bump" and
                str(cmd.get("application_id")) == DISBOARD_APP_ID
            ):
                return cmd
    return None


def make_session_id() -> str:
    return ''.join(random.choices(string.hexdigits[:16].lower(), k=32))


async def send_bump(session: aiohttp.ClientSession, guild_id: str, command: dict) -> int:
    payload = {
        "type": 2,
        "application_id": DISBOARD_APP_ID,
        "guild_id": guild_id,
        "channel_id": str(BUMP_CHANNEL_ID),
        "session_id": make_session_id(),
        "data": {
            "version":             command["version"],
            "id":                  command["id"],
            "name":                "bump",
            "type":                1,
            "application_command": command,
            "attachments":         []
        }
    }

    async with session.post(
        "https://discord.com/api/v9/interactions",
        headers=HEADERS,
        json=payload
    ) as resp:
        log.info(f"Interaction POST → {resp.status}")
        return resp.status


async def main():
    async with aiohttp.ClientSession() as session:

        # fetch guild id once
        guild_id = await get_guild_id(session)
        log.info(f"Guild ID resolved: {guild_id}")

        while True:
            try:
                state        = read_state()
                now          = time.time()
                cycle_index  = state.get("cycle_index", 0)
                last_bump    = state.get("last_bump_time", 0)
                interval     = CYCLE_INTERVALS[cycle_index % 3]
                elapsed      = now - last_bump
                remaining    = interval - elapsed

                log.info(
                    f"Cycle {cycle_index % 3} | "
                    f"Interval {interval/3600:.2f}h | "
                    f"Elapsed {elapsed/3600:.2f}h | "
                    f"Remaining {max(remaining,0)/3600:.2f}h"
                )

                if elapsed >= interval:
                    command = await get_bump_command(session, guild_id)

                    if not command:
                        log.warning("Could not find Disboard /bump command. Retrying in 5 min.")
                        await asyncio.sleep(300)
                        continue

                    status = await send_bump(session, guild_id, command)

                    if status == 204:
                        log.info(f"✅ Bump successful! Next cycle: {(cycle_index + 1) % 3}")
                        state["last_bump_time"] = now
                        state["cycle_index"]    = (cycle_index + 1) % 3
                        state["reminder_sent"]  = False
                        write_state(state)
                    else:
                        log.warning(f"Bump returned {status}. Will retry next check.")

            except Exception as e:
                log.error(f"Error in selfbot loop: {e}")

            # check every 60 seconds
            await asyncio.sleep(60)


asyncio.run(main())
