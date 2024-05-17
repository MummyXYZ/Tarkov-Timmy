from __future__ import annotations

import discord
import utils.db as db
from discord import Embed
from utils.checkperms import checkperms as CP
from utils.embedbuilder import embedbuilder as EB

import logging
import logging.handlers

logger = logging.getLogger("discord")


class removeSC:
    async def remove(interaction: discord.Interaction, id: int) -> None:
        # Permission Check
        if not await CP(interaction, "remove"):
            return

        guild = interaction.guild
        desc = ""

        query = """SELECT id, killer_id, killed_id, date, description, video_link FROM tk_entries WHERE guild_id = %s AND id = %s"""
        params = (guild.id, id)

        try:
            result = await db.query(query, params)

            if not result:
                desc += f"The ID: **{id}** doesn't exist."
            else:
                if not result[0][5]:
                    desc += f"**ID: {id}.** <@{result[0][1]}> killed <@{result[0][2]}> Description: **{result[0][4]}**.\nHas been removed from the database."
                else:
                    desc += f"**ID: {id}.** <@{result[0][1]}> killed <@{result[0][2]}> Description: [**{result[0][4]}**]({result[0][5]}).\nHas been removed from the database."

                query = """DELETE FROM tk_entries WHERE guild_id = %s AND id = %s"""
                params = (guild.id, id)

                await db.query(query, params)

            embed = await EB(
                title="Team Kill Removed", description=desc, timestamp=True
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Remove error, {e}")
            embed: Embed = await EB(
                title="Error Occured",
                description="There has been an error. Please contact MummyX#2616.",
            )

            await interaction.followup.send(embed=embed)
