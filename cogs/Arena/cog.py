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

    maps = []
    with open("./configs/conf.json", "r") as f:
        conf = json.load(f)

    for location in conf["arena_Locations"]:
        maps.append(Choice(name=location, value=location))

    @app_commands.command(
        name="map",
        description="Maps and information for EFT: Arena",
        # Help description of the command
        extras=[
            """Displays maps and information for maps on EFT: Arena.
            
            **E.g.** </arena map:1253013351018266729> <Block>\n(*<> are required*)""",
        ],
    )
    @app_commands.describe(map="Specify the map", hidden="Hide message?")
    @app_commands.choices(map=maps)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def map(
        self, interaction: discord.Interaction, map: str, hidden: bool = True
    ) -> None:
        await mapSC.map(interaction, map, hidden)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Arena(bot))
