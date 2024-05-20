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
        # Permission Check
        if not await CP(interaction, "edit"):
            return

        if category == "video_link":
            # Validate URL for embeding Ex.(✅: "https://google.com" ❌: google.com)
            if not validators.url(value):
                await interaction.response.defer(ephemeral=True)
                embed: Embed = EB(
                    title="Input Error", description="Invalid URL, please try again."
                )
                await interaction.followup.send(embed=embed)
                return
            query = """UPDATE tk_entries SET video_link = %s WHERE id = %s && guild_id = %s"""
            category = "video link"
        else:
            query = """UPDATE tk_entries SET description = %s WHERE id = %s && guild_id = %s"""
            category = "description"

        guild = interaction.guild
        desc = ""
        params = (value, id, guild.id)

        try:
            result = await db.query(query, params)
            if result == 0:
                desc += (
                    f"The ID: **{id}** either doesn't exist or had a duplicate value."
                )
            else:
                desc += f"**ID: {id}**'s **{category}** has been changed to {value}."

            embed: Embed = EB(
                title="Team Kill Edited", description=desc, timestamp=datetime.now()
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Edit error, {e}")
            embed: Embed = EB(
                title="Error Occured",
                description="There has been an error. Please contact MummyX#2616.",
            )

            await interaction.followup.send(embed=embed)
