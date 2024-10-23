from __future__ import annotations

import discord
import json
from discord import Embed
from utils.embedbuilder import embedbuilder as EB
import logging
import logging.handlers

logger = logging.getLogger("discord")

class mapSC:
    @staticmethod
    async def map(interaction: discord.Interaction, map: str, hidden: bool) -> None:
        await interaction.response.defer(ephemeral=hidden)

        # Load the configuration file
        try:
            with open("./configs/conf.json", "r") as f:
                conf = json.load(f)
        except FileNotFoundError:
            logger.error("Configuration file not found.")
            await interaction.followup.send("Error: Configuration file not found.", ephemeral=True)
            return
        except json.JSONDecodeError:
            logger.error("Error parsing configuration file.")
            await interaction.followup.send("Error: Configuration file is corrupted.", ephemeral=True)
            return

        # Check if the map exists in the configuration
        if map not in conf.get("arena_Locations", {}):
            logger.warning(f"Map '{map}' not found in the configuration.")
            await interaction.followup.send(f"Map '{map}' not found.", ephemeral=True)
            return

        map_info = conf["arena_Locations"][map]
        image_url = f"{map_info['base']}/revision/latest/scale-to-width-down/800"
        map_format = map.replace(" ", "_")
        url = f"https://escapefromtarkov.fandom.com/wiki/Arena#{map_format}"

        embed: Embed = EB(
            title=map,
            title_url=url,
            description=f"[**Hi-res Here**]({map_info['base']})",
            image_url=image_url,
        )

        await interaction.followup.send(embed=embed, ephemeral=hidden)
