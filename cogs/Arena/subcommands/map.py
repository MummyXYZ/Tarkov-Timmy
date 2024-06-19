from __future__ import annotations


import discord
import json
from discord import Embed
from utils.embedbuilder import embedbuilder as EB
import logging
import logging.handlers

logger = logging.getLogger("discord")


class mapSC:
    async def map(interaction: discord.Interaction, map, hidden) -> None:
        await interaction.response.defer(ephemeral=hidden)

        # Load the configuration file
        with open("./configs/conf.json", "r") as f:
            conf = json.load(f)

        image = f"{conf['arena_Locations'][map]['base']}/revision/latest/scale-to-width-down/800"

        map_Format = map.replace(" ", "_")

        url = f"https://escapefromtarkov.fandom.com/wiki/Arena#{map_Format}"

        embed: Embed = EB(
            title=map,
            title_url=url,
            description=f"[**Hi-res Here**]({conf['arena_Locations'][map]['base']})",
            image_url=image,
            footer="Deletes in 5 mins",
        )

        message: discord.Message = await interaction.followup.send(
            embed=embed,
            ephemeral=True,
        )
        await message.delete(delay=300)
