from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from .time_view import TimeView


class Time(commands.Cog, name="time"):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TimeView())

    @app_commands.command(name="time", description="Current in-game raid time")
    async def time(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(view=TimeView())


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Time(bot))
