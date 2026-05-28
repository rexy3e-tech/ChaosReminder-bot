import discord
import asyncio
import time
import logging

from config import REMINDER_BOT_TOKEN, BUMP_CHANNEL_ID, BUMP_ROLE_ID, REMINDER_OFFSET
from state_manager import read_state, write_state

logging.basicConfig(
    level=logging.INFO,
    format="[REMINDER] %(asctime)s %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

intents = discord.Intents.default()
client  = discord.Client(intents=intents)


@client.event
async def on_ready():
    log.info(f"Logged in as {client.user}")
    client.loop.create_task(reminder_loop())


async def reminder_loop():
    await client.wait_until_ready()
    channel = client.get_channel(BUMP_CHANNEL_ID)

    if not channel:
        log.error(f"Could not find channel {BUMP_CHANNEL_ID}. Check BUMP_CHANNEL_ID.")
        return

    while not client.is_closed():
        try:
            state   = read_state()
            now     = time.time()
            elapsed = now - state["last_bump_time"]
            already_reminded = state.get("reminder_sent", False)

            if elapsed >= REMINDER_OFFSET and not already_reminded:
                role    = channel.guild.get_role(BUMP_ROLE_ID)
                mention = role.mention if role else "@bump"
                await channel.send(f"{mention} bump now")
                log.info("Reminder sent.")

                state["reminder_sent"] = True
                write_state(state)

        except Exception as e:
            log.error(f"Error in reminder loop: {e}")

        await asyncio.sleep(30)   # check every 30 seconds


client.run(REMINDER_BOT_TOKEN)
