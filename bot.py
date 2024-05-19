from __future__ import annotations

import os
import discord
from datetime import datetime
from discord.ext import commands
import utils.guildhandler as GH
from dotenv import load_dotenv

import logging
import logging.handlers

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

load_dotenv()


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

    async def on_connect(self) -> None:
        logger.info("Connected to Discord gateway!")

    async def on_ready(self):
        await self.wait_until_ready()
        logger.info(f"{self.user.display_name} is ready!")

    async def on_guild_join(self, guild: discord.Guild):
        await GH.create(guild)

    async def on_guild_remove(self, guild: discord.Guild):
        await GH.delete(guild)

    async def on_member_join(self, member: discord.Member):
        pass

    async def on_member_remove(self, member: discord.Member):
        pass

    async def on_command_error(self, ctx, error):
        pass


if __name__ == "__main__":
    bot = Bot()
    if os.getenv("RUNTIME") == "DEV":
        bot.run(os.getenv("DEV_TOKEN"))
    else:
        bot.run(os.getenv("TOKEN"))
