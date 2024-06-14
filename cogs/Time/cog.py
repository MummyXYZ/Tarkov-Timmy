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

    @app_commands.command(
        name="time",
        # Short description of the command
        description="Current in-game raid time",
        # Help description of the command
        extras=[
            """Displays a button thats label has in-game Tarkov time. Press the button to refresh the time.
            
            **E.g.** </time:1241780138593616022>""",
        ],
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def time(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(view=TimeView())


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Time(bot))
