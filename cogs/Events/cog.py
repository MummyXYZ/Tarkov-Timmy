from __future__ import annotations

import discord
from discord.ext import commands
import utils.guildhandler as GH


import logging
import logging.handlers

logger = logging.getLogger("discord")


class Events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        logger.info(f"{self.bot.user.display_name} is ready!")

    async def on_connect(self) -> None:
        logger.info("Connected to Discord gateway!")

    async def on_guild_join(self, guild: discord.Guild):
        await GH.create(guild)

    async def on_guild_remove(self, guild: discord.Guild):
        await GH.delete(guild)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Events(bot))
