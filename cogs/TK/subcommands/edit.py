from __future__ import annotations

import discord
import validators
import utils.db as db
from discord import Embed
from datetime import datetime
from utils.checkperms import checkperms as CP
from utils.embedbuilder import embedbuilder as EB

import logging
import logging.handlers

logger = logging.getLogger("discord")


class editSC:
    async def edit(
        interaction: discord.Interaction, id: int, category: str, value: str
    ) -> None:
        await interaction.response.defer()
        # Permission Check
        if not await CP(interaction, "edit"):
            return

        if category == "video_link":
            # Validate URL for embeding Ex.(✅: "https://google.com" ❌: google.com)
            if not validators.url(value):
                embed: Embed = EB(
                    title="Input Error", description="Invalid URL, please try again."
                )
                await interaction.followup.send(embed=embed)
                return
            query = (
                "UPDATE tk_bot.entries SET video_link=$1 WHERE id=$2 AND guild_id=$3"
            )
            category = "video link"
        else:
            query = (
                "UPDATE tk_bot.entries SET description=$1 WHERE id=$2 AND guild_id=$3"
            )
            category = "description"

        params = (value, id, interaction.guild.id)
        desc = ""
        result = await db.execute(query, *params)

        if result == "0":
            desc += f"The ID: **{id}** either doesn't exist."
        else:
            desc += f"**ID: {id}**'s **{category}** has been changed to {value}."

        embed: Embed = EB(
            title="Team Kill Edited", description=desc, timestamp=datetime.now()
        )
        await interaction.followup.send(embed=embed)
