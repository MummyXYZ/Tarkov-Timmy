from __future__ import annotations

import os
import discord
import asyncio
import logging
import logging.handlers
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.handlers.TimedRotatingFileHandler(
    "log/discord.log",
    when="midnight",
    backupCount=10,
    encoding="utf-8",
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


async def run():
    bot = Bot()
    if os.getenv("RUNTIME") == "DEV":
        await bot.start(os.getenv("DEV_TOKEN"))
    else:
        await bot.start(os.getenv("TOKEN"))


class Bot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

        self.init_extensions = []
        for folder in os.listdir("./cogs"):
            if os.path.exists(os.path.join("cogs", folder, "cog.py")):
                self.init_extensions.append(f"cogs.{folder}.cog")

    async def setup_hook(self: Bot) -> None:
        for extension in self.init_extensions:
            await self.load_extension(extension)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()

    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        loop.close()
