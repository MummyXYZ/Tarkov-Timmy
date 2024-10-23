from __future__ import annotations

import discord
import os
from discord import Embed, app_commands
from discord.ext import commands
from datetime import datetime
from utils.embedbuilder import embedbuilder as EB
import logging
import logging.handlers

logger = logging.getLogger("discord")


class About(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        self.startTime = datetime.now()

    @app_commands.command(
        name="about",
        description="Information about the bot",
        extras=[
            """Displays information about Tarkov Timmy.
            
            **E.g.** </about:1241780138593616027>""",
        ],
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def about(self, interaction: discord.Interaction):
        await interaction.response.defer()

        start_timestamp = int(self.startTime.timestamp())

        updated = os.getenv("UPDATED", "Unknown")

        users = sum(guild.member_count for guild in self.bot.guilds)

        embed: Embed = EB(
            title="About:",
            description=(
                "A Discord bot that helps you in Escape From Tarkov and a tool to have fun with friends, "
                "providing information quickly for your raids. Operated with simple and easy-to-use slash commands.\n"
                "To get started, try </help:1067035934073290795>\n\n"
                "For support, join [my support server](https://discord.gg/CC9v5aXNyY)"
            ),
            footer=f"Made with discord.py || Last updated: {updated}",
            footer_icon="https://www.iconattitude.com/icons/open_icon_library/apps/png/256/python2.5.png",
        )

        embed.add_field(name="Members", value=f"{users} total")
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds)}")
        embed.add_field(name="Uptime", value=f"<t:{start_timestamp}:R>")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(About(bot))
