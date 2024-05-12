from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from .time_view import TimeView

import json, requests

class Time(commands.Cog, name = "time"):


    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TimeView())

    @app_commands.command(name= "time", description = "Current in-game raid time")
    async def time(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(view = TimeView())

    # @app_commands.command(name= "time", description = "Current in-game raid time")
    # async def time(self, interaction: discord.Interaction):
    #     await interaction.response.defer()
    #     ammoJson = json.dumps((requests.get("https://api.tarkov-changes.com/v1/ammo", headers={"User-Agent": "Mozilla/5.0", "AUTH-TOKEN":"546736a7500f92a94caf"}, ).json())['results'])
    #     # ammoJson = requests.get("https://api.tarkov-changes.com/v1/ammo", headers={"User-Agent": "Mozilla/5.0", "AUTH-TOKEN":"546736a7500f92a94caf"}).json()
    #     # print(ammoJson)

    #     with open("./temp.json", "w") as f:
    #         f.write(ammoJson)
    #         f.close()
    #     await interaction.followup.send(content="Done")

    
async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Time(bot))