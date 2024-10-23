from __future__ import annotations

import discord
import json
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from .subcommands.map import mapSC


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
class Arena(commands.GroupCog, name="arena"):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        super().__init__()
        # Load maps data during initialization
        with open("./configs/conf.json", "r") as f:
            self.maps = json.load(f)["arena_Locations"]

    # Autocomplete function for map selection
    async def map_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[Choice[str]]:
        # Filter map choices based on user input and limit to 25
        return [
            Choice(name=location, value=location)
            for location in self.maps
            if current.lower() in location.lower()
        ][:25]

    @app_commands.command(
        name="map",
        description="Maps and information for EFT: Arena",
        extras=[
            """Displays maps and information for maps on EFT: Arena.
            
            **E.g.** </arena map:1253013351018266729> <Block> (*<> are required*)""",
        ],
    )
    @app_commands.describe(map="Specify the map", hidden="Hide message?")
    @app_commands.autocomplete(map=map_autocomplete)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def map(self, interaction: discord.Interaction, map: str, hidden: bool = True) -> None:
        await mapSC.map(interaction, map, hidden)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Arena(bot))
