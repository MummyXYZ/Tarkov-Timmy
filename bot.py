from __future__ import annotations

import os
import discord
import asyncio
import logging
import logging.handlers
import utils.db as db
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

log_level = os.getenv("LOG_LEVEL", "INFO")

logger = logging.getLogger("discord")
logger.setLevel(log_level)
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
    token = os.getenv("TOKEN")

    if not token:
        raise RuntimeError("TOKEN not found in environment variables.")

    try:
        await bot.start(token)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("Tarkov Timmy is shutting down gracefully...")
        await bot.close()
    finally:
        await asyncio.sleep(1)


class Bot(commands.AutoShardedBot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix="!",
                         intents=intents,
                         help_command=None)

        self.init_extensions = [
            f"cogs.{folder}.cog" for folder in os.listdir("./cogs")
            if os.path.exists(os.path.join("cogs", folder, "cog.py"))
        ]

    async def setup_hook(self: Bot) -> None:
        await db.create_pool()
        logger.info("Database pool initialized!")

        for extension in self.init_extensions:
            await self.load_extension(extension)


if __name__ == "__main__":
    asyncio.run(run())
