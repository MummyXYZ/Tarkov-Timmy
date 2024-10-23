from __future__ import annotations

import discord
import json
from discord import Embed, app_commands
from discord.ext import commands
from discord.app_commands import Choice
from .map_view import MapView
from utils.embedbuilder import embedbuilder as EB


class Map(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        self.maps = self.load_map_choices()

    @staticmethod
    def load_map_choices() -> list[Choice[str]]:
        """Load map choices from configuration files."""
        with open("./configs/conf.json", "r") as f:
            conf = json.load(f)

        with open("./configs/data/maps.json", "r") as f:
            maps_json = json.load(f)

        return [
            Choice(name=map_data["name"], value=map_data["name"])
            for map_data in maps_json
            if map_data["name"] in conf["locations"]
        ]

    @app_commands.command(
        name="map",
        description="Maps and information for a specific location",
        extras=[
            """Displays maps and information for a specified map with buttons for additional information at the bottom.
            
            **E.g.** </map:1241780138593616025> <Customs> (*<> are required*)""",
        ],
    )
    @app_commands.describe(map="Specify the map", hidden="Hide message?")
    @app_commands.choices(map=load_map_choices())
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def map(
        self, interaction: discord.Interaction, map: str, hidden: bool = True
    ):
        await interaction.response.defer(ephemeral=hidden)

        # Load configuration files
        conf, maps_json = self.load_configuration_files()

        map_data = self.get_map_data(map, maps_json)
        if not map_data:
            await interaction.followup.send(f"Map '{map}' not found.", ephemeral=True)
            return

        embed = self.build_map_embed(map, map_data, conf)
        message: discord.Message = await interaction.followup.send(
            embed=embed,
            view=MapView(map, conf, maps_json),
            ephemeral=True,
        )
        await message.delete(delay=300)

    @staticmethod
    def load_configuration_files():
        """Load configuration and map data from JSON files."""
        with open("./configs/conf.json", "r") as f:
            conf = json.load(f)

        with open("./configs/data/maps.json", "r") as f:
            maps_json = json.load(f)

        return conf, maps_json

    @staticmethod
    def get_map_data(map_name: str, maps_json: list[dict]) -> dict | None:
        """Retrieve map data for the given map name."""
        map_name = "Ground Zero 21+" if map_name == "Ground Zero" else map_name
        for map_data in maps_json:
            if map_data["name"] == map_name:
                return map_data
        return None

    def build_map_embed(self, map: str, map_data: dict, conf: dict) -> Embed:
        """Create an embed for the specified map."""
        # Extract map details
        duration = f"{map_data['raidDuration']} Mins"
        players = map_data["players"]
        flavor = map_data["description"]
        url = map_data["wiki"]

        # Build boss information
        boss_data = self.build_boss_data(map_data)

        # Format description
        description = self.build_description(boss_data)

        # Build image URL
        image_url = (
            f"{conf['locations'][map]['base']}/revision/latest/scale-to-width-down/800"
        )

        # Create the embed
        embed = EB(
            title=map,
            title_url=url,
            description=description,
            image_url=image_url,
            footer=f"{flavor}\n\nDeletes in 5 mins",
        )
        embed.add_field(inline=True, name="Duration", value=duration)
        embed.add_field(inline=True, name="Players", value=players)
        embed.add_field(inline=True, name="The Goons", value=boss_data["goons"])
        embed.add_field(inline=True, name="Cultists", value=boss_data["cult"])

        return embed

    @staticmethod
    def build_boss_data(map_data: dict) -> dict:
        """Extract and format boss-related data from map data."""
        boss_data = {"name": [], "chance": [], "escorts": [], "cult": False, "goons": False}

        for boss in map_data.get("bosses", []):
            not_boss = {"Raider", "Rogue"}
            boss_name = boss["boss"]["name"]

            if boss_name in not_boss:
                continue
            if boss_name == "Cultist Priest":
                boss_data["cult"] = True
                continue
            if boss_name == "Knight":
                boss_data["goons"] = True
                continue

            boss_data["name"].append(
                f"[{boss_name}](https://escapefromtarkov.fandom.com/wiki/{boss_name})"
            )
            boss_data["chance"].append(f"{int(boss['spawnChance'] * 100)}%")

            # Add escort count
            escort_count = boss["escorts"][0]["amount"][0]["count"] if boss["escorts"] else "0"
            boss_data["escorts"].append(str(escort_count))

        return boss_data

    @staticmethod
    def build_description(boss_data: dict) -> str:
        """Build the description field for the map embed based on boss data."""
        if not boss_data["name"]:
            return ""

        description = (
            f"**Boss:** {', '.join(boss_data['name'])}\n"
            f"**Spawn Chance:** {', '.join(boss_data['chance'])}"
        )
        if boss_data["escorts"]:
            description += f"\n**Followers:** {', '.join(boss_data['escorts'])}"
        return description


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Map(bot))
