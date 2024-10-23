from __future__ import annotations

import discord
import utils.db as db
from utils.checkperms import checkperms as CP
from utils.embedbuilder import embedbuilder as EB
import logging
import logging.handlers

logger = logging.getLogger("discord")


class removeSC:
    async def remove(interaction: discord.Interaction, id: int) -> None:
        await interaction.response.defer()

        # Permission Check
        if not await CP(interaction, "remove"):
            return

        guild = interaction.guild

        # Fetch Guild Icon and Member Count
        guild_icon_url = guild.icon.url if guild.icon else None
        guild_member_count = guild.member_count

        try:
            async with db.pool.acquire() as cxn:
                async with cxn.transaction():
                    # Update Guild Information in the 'guilds' table
                    query = """
                        INSERT INTO tk_bot.guilds (guild_id, guild_name, guild_icon, member_count)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (guild_id) DO UPDATE 
                        SET guild_name = EXCLUDED.guild_name, 
                            guild_icon = EXCLUDED.guild_icon, 
                            member_count = EXCLUDED.member_count
                    """
                    params = (guild.id, guild.name, guild_icon_url, guild_member_count)
                    await cxn.execute(query, *params)

                    # Perform DELETE with RETURNING to fetch and delete in one query
                    query = """
                        DELETE FROM tk_bot.entries
                        WHERE guild_id = $1 AND id = $2
                        RETURNING id, killer_id, killed_id, description, video_link
                    """
                    params = (guild.id, id)
                    result = await cxn.fetch(query, *params)

                    # Prepare the response description
                    desc = ""
                    if not result:
                        desc += f"The ID: **{id}** doesn't exist."
                    else:
                        entry = result[0]
                        if entry["video_link"]:  # Video link present
                            desc += f"**ID: {id}.** <@{entry['killer_id']}> killed <@{entry['killed_id']}> Description: [**{entry['description']}**]({entry['video_link']}).\nHas been removed from the database."
                        else:  # No video link
                            desc += f"**ID: {id}.** <@{entry['killer_id']}> killed <@{entry['killed_id']}> Description: **{entry['description']}**.\nHas been removed from the database."

        except Exception as e:
            logger.error(f"Error removing entry: {e}")
            await interaction.followup.send("An error occurred while removing the entry.")
            return

        # Send the success message
        embed = EB(title="Team Kill Removed", description=desc, timestamp=True)
        await interaction.followup.send(embed=embed)
