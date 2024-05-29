from __future__ import annotations

import discord
import requests
from datetime import datetime
from discord import app_commands, Embed
from discord.ext import commands
from utils.embedbuilder import embedbuilder as EB


class Goons(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @app_commands.command(
        name="goons",
        description="Display community provided information of where the Goons may be spawning",
    )
    async def map(self, interaction: discord.Interaction):
        await interaction.response.defer()

        data = requests.get(
            "https://tarkovpal.com/api",
            headers={"User-Agent": "Mozilla/5.0"},
        ).json()

        timestamp = int(
            datetime.strptime(data["Time"][0], "%b %d, %Y, %I:%M %p").timestamp()
        )

        embed: Embed = EB(
            title="Goons Sightings",
            description="The most recent Goons sighting from TarkovPal.com",
            footer="Powered by TarkovPal.com",
            footer_icon="https://tarkovpal.com/logov2.png",
        )

        embed.add_field(
            name="Map",
            value=data["Current Map"][0],
        )
        embed.add_field(name="Last Seen", value=f"<t:{timestamp}:t>")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Goons(bot))
