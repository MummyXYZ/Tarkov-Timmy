from __future__ import annotations

import os
import discord
import logging
import logging.handlers
from discord.ext import commands

import utils.db as db

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
    bot = Bot()
    if os.getenv("RUNTIME") == "DEV":
        bot.run(os.getenv("DEV_TOKEN"))
    else:
        bot.run(os.getenv("TOKEN"))
