from __future__ import annotations

import discord, json
from discord import Embed, app_commands
from discord.ext import commands
from utils.embedbuilder import embedbuilder as EB

VIEW_NAME = "HelpView"

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        with open('./configs/commands/help.json', 'r') as f:
            help = json.load(f)
        for command in help:
            self.add_item(HelpButton(command))

class HelpButton(discord.ui.Button):
    def __init__(self, label):
        super().__init__(style= discord.ButtonStyle.primary, label=label, custom_id=f"{VIEW_NAME} - {label}")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        with open('./configs/commands/help.json', 'r') as f:
            help = json.load(f)
        cID = self.custom_id.split(" - ", 1)[1]
        desc = help[cID][1]
        embed = await EB(
            title=f"{help[cID][0]} Help",
            description=desc
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

class Help(commands.Cog, name = "help"):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(HelpView())

    @app_commands.command(description = "Help for the various commands of the TK Bot")
    @app_commands.describe(hidden="Hide message?")
    async def help(self, interaction: discord.Interaction, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)
        embed:Embed = await EB(
            title="Help",
            description=f"Please select one of the commands below to receive more information about it and examples.",
        )

        await interaction.followup.send(embed=embed, view=HelpView(), ephemeral=hidden)

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Help(bot))