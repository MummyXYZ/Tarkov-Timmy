from __future__ import annotations

import discord
import json
from discord import Embed
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from .map_view import MapView
from utils.embedbuilder import embedbuilder as EB


class Map(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    maps = []
    with open("./configs/conf.json", "r") as f:
        conf = json.load(f)

    with open("./configs/data/maps.json", "r") as f:
        mapsJson = json.load(f)

    for location in conf["locations"]:
        for map in mapsJson:
            if location == map["name"]:
                maps.append(Choice(name=map["name"], value=map["name"]))

    @app_commands.command(
        name="map",
        description="Maps and information for a specific location",
        # Help description of the command
        extras=[
            """Displays maps and information for a specified map with buttons for additional information at the bottom.
            
            **E.g.** </map:1241780138593616025> <Customs>\n(*<> are required*)""",
        ],
    )
    @app_commands.describe(map="Specify the map", hidden="Hide message?")
    @app_commands.choices(map=maps)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def map(
        self, interaction: discord.Interaction, map: str, hidden: bool = True
    ):
        await interaction.response.defer(ephemeral=hidden)

        # Load the configuration file
        with open("./configs/conf.json", "r") as f:
            conf = json.load(f)

        # Load the maps JSON file
        with open("./configs/data/maps.json", "r") as f:
            mapsJson = json.load(f)

        # Initialize the description variable
        description = ""

        # Initialize the boss data dictionary
        bossData = {
            "name": [],  # List to store boss names
            "chance": [],  # List to store boss spawn chances
            "escorts": [],  # List to store escort names
            "cult": False,  # Bool to store whether the map has Cultists
            "goons": False,  # Bool to store whether the map has The Goons
        }

        # Iterate through the mapsJson data
        for mapData in mapsJson:
            # Check if the map is Ground Zero and assign the appropriate mapName
            if map == "Ground Zero":
                mapName = "Ground Zero 21+"
            else:
                mapName = map

            # Check if the mapName matches the current mapData
            if mapData["name"] == mapName:
                # Extract necessary information from mapData
                duration = f"{mapData['raidDuration']} Mins"
                players = mapData["players"]
                flavor = mapData["description"]
                url = mapData["wiki"]

                # Iterate through the bosses in the current mapData
                for boss in mapData["bosses"]:
                    # Define a set of boss names to skip
                    notBoss = {"Raider", "Rogue"}

                    # Skip the boss if it is in the notBoss set
                    if boss["boss"]["name"] in notBoss:
                        continue

                    # Check if the boss is a Cultist Priest or Death Knight
                    if boss["boss"]["name"] == "Cultist Priest":
                        # Set the cult flag to True and continue to the next boss
                        bossData["cult"] = True
                        continue
                    if boss["boss"]["name"] == "Death Knight":
                        # Set the goons flag to True and continue to the next boss
                        bossData["goons"] = True
                        continue

                    # Add the boss name to the bossData dictionary with a link to its wiki page
                    bossData["name"].append(
                        f"[{boss['boss']['name']}](https://escapefromtarkov.fandom.com/wiki/{boss['boss']['name']})"
                    )

                    # Add the spawn chance to the bossData dictionary
                    bossData["chance"].append(f"{int(boss['spawnChance'] * 100)}%")
                    # Check if the boss has escorts
                    if len(boss["escorts"]) > 0:
                        # Get the count of the first escort
                        escort_count = boss["escorts"][0]["amount"][0]["count"]
                        # Add the escort count to the bossData dictionary
                        bossData["escorts"].append(str(escort_count))
                    else:
                        # If the boss does not have escorts, add "0" to the bossData dictionary
                        bossData["escorts"].append("0")

        # Format the description based on the bossData dictionary
        if len(bossData["name"]) != 0:
            description = f"**Boss:** {', '.join(bossData['name'])}\n**Spawn Chance:** {', '.join(bossData['chance'])}"
            # Check if the boss has escortss
            if len(boss["escorts"]) > 0:
                description += f"\n**Followers:** {', '.join(bossData['escorts'])}"

        image = (
            f"{conf['locations'][map]['base']}/revision/latest/scale-to-width-down/800"
        )

        embed: Embed = EB(
            title=map,
            title_url=url,
            description=description,
            image_url=image,
            footer=flavor,
        )

        embed.add_field(inline=True, name="Duration", value=duration)
        embed.add_field(inline=True, name="Players", value=players)
        embed.add_field(
            inline=True, name="The Goons", value=True if bossData["goons"] else False
        )
        embed.add_field(
            inline=True, name="Cultists", value=True if bossData["cult"] else False
        )

        await interaction.followup.send(
            embed=embed, view=MapView(map, conf, mapsJson), ephemeral=True
        )


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Map(bot))
