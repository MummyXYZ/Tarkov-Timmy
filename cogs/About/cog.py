from __future__ import annotations

import discord, json, os
from discord import Embed, app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from utils.embedbuilder import embedbuilder as EB

class About(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        self.startTime = ''

    @app_commands.command(name= "about", description = "Information about the bot")
    async def about(self, interaction: discord.Interaction):
        await interaction.response.defer()

        delta:timedelta = datetime.now() - self.startTime

        seconds = int(delta.total_seconds())
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours >= 24:
            days, hours = divmod(hours, 24)
            uptime = f"{days}d {hours}h {minutes}m {seconds}s"
        else:
            uptime = f"{hours}h {minutes}m {seconds}s"
        
        with open('./configs/data/about.json', 'r') as f:
            aboutJson = json.load(f)

        updated = os.getenv("UPDATED")

        embed:Embed = await EB(
            title="About:",
            description=f"A Discord bot that helps you in Escape From Tarkov and a tool to have fun with friends and provide information quickly for your raids. Operated with simple and easy to use slash commands.\nTo get started try </help:1067035934073290795>",
            footer=f"Made with discord.py || Last updated : {updated}",
            footer_icon="https://www.iconattitude.com/icons/open_icon_library/apps/png/256/python2.5.png"
        )

        embed.add_field(name="Members", value=f"{aboutJson['users']} total\n{aboutJson['uniqueUsers']} unique")
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds)}")
        embed.add_field(name="Uptime", value=f"{uptime}")


        await interaction.followup.send(embed=embed)

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(About(bot))