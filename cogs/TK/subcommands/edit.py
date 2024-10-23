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

        guild = interaction.guild

        # Fetch Guild Icon and Member Count
        guild_icon_url = guild.icon.url if guild.icon else None
        guild_member_count = guild.member_count

        try:
            # Perform all queries within a single transaction
            async with db.pool.acquire() as cxn:
                async with cxn.transaction():

                    # Update the Guild's name, icon URL, and member count in the 'guilds' table
                    query = """
                        INSERT INTO tk_bot.guilds (guild_id, guild_name, guild_icon, member_count)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (guild_id) DO UPDATE 
                        SET guild_name = EXCLUDED.guild_name, 
                            guild_icon = EXCLUDED.guild_icon, 
                            member_count = EXCLUDED.member_count
                    """
                    params = (guild.id, guild.name,
                              guild_icon_url, guild_member_count)
                    await cxn.execute(query, *params)

                    # Edit the entry based on the category
                    if category == "video_link":
                        # Validate URL for embedding (e.g., "https://google.com" is valid, "google.com" is not)
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

                    # Execute the update query and check the result
                    result = await cxn.execute(query, *params)

                    desc = ""
                    if result == "0":
                        desc += f"The ID: **{id}** either doesn't exist."
                    else:
                        desc += f"**ID: {id}**'s **{category}** has been changed to {value}."

                    embed: Embed = EB(
                        title="Team Kill Edited", description=desc, timestamp=datetime.now()
                    )
                    await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error editing entry: {e}")
            await interaction.followup.send("An error occurred while editing the entry.")
