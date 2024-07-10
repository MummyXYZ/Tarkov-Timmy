from __future__ import annotations

import discord
import os
from discord import Embed, app_commands
from discord.ext import commands
from datetime import datetime, timedelta
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
        # Short description of the command
        description="Information about the bot",
        # Help description of the command
        extras=[
            """Displays information about Tarkov Timmy.
            
            **E.g.** </about:1241780138593616027>""",
        ],
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def about(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.bot.wait_until_ready()

        delta: timedelta = datetime.now() - self.startTime

        seconds = int(delta.total_seconds())
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours >= 24:
            days, hours = divmod(hours, 24)
            uptime = f"{days}d {hours}h {minutes}m {seconds}s"
        else:
            uptime = f"{hours}h {minutes}m {seconds}s"

        updated = os.getenv("UPDATED")

        users = sum(
            [self.bot.get_guild(guild.id).member_count for guild in self.bot.guilds]
        )
        aboutJson = {"users": users}
        # , "uniqueUsers": len(self.bot.users)}

        embed: Embed = EB(
            title="About:",
            description="A Discord bot that helps you in Escape From Tarkov and a tool to have fun with friends and provide information quickly for your raids. Operated with simple and easy to use slash commands.\nTo get started try </help:1067035934073290795>\n\nFor support join [my support server](https://discord.gg/CC9v5aXNyY)",
            footer=f"Made with discord.py || Last updated : {updated}",
            footer_icon="https://www.iconattitude.com/icons/open_icon_library/apps/png/256/python2.5.png",
        )

        embed.add_field(
            name="Members",
            value=f"{aboutJson['users']} total",
            # \n{aboutJson['uniqueUsers']} unique",
        )
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds)}")
        embed.add_field(name="Uptime", value=f"{uptime}")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(About(bot))
