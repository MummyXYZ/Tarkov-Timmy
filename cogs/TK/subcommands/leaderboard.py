from __future__ import annotations

import discord
import utils.db as db
from utils.ButtonMenu import ButtonMenu
from utils.checkperms import checkperms as CP
from utils.embedbuilder import embedbuilder as EB
import logging
import logging.handlers

logger = logging.getLogger("discord")


class leaderboardSC:
    async def leaderboard(interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        # Permission Check
        if not await CP(interaction, "leaderboard"):
            return

        guild = interaction.guild

        # Fetch Guild Icon, Member Count
        guild_icon_url = guild.icon.url if guild.icon else None
        guild_member_count = guild.member_count

        try:
            async with db.pool.acquire() as cxn:
                async with cxn.transaction():
                    # Update the Guild's information in the 'guilds' table
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

                    # SQL query to get the leaderboard
                    query = """
                        SELECT killer_id, COUNT(killer_id) AS count
                        FROM tk_bot.entries
                        WHERE guild_id = $1
                        GROUP BY killer_id
                        ORDER BY count DESC
                    """
                    params = (guild.id,)
                    result = await cxn.fetch(query, *params)

        except Exception as e:
            logger.error(f"Error updating guild data: {e}")
            await interaction.followup.send("An error occurred while updating the guild data.")

        # Prepare the description and embed pages
        descs, pages = [], []
        if not result:
            descs.append("No TKs on this server.")
        else:
            page_content = []
            for count, entry in enumerate(result, 1):
                page_content.append(f"<@{entry[0]}> - **{entry[1]}**")

                # Every 10 items, start a new page
                if count % 10 == 0 or count == len(result):
                    descs.append("\n".join(page_content))
                    page_content = []

        # Create an embed for each page of results
        for desc in descs:
            pages.append(
                EB(title=f"{guild.name} Leaderboard", description=desc))

        # Create a ButtonMenu for pagination if there are multiple pages
        view = ButtonMenu(pages, timeout=120)

        # Send the message with or without pagination
        if len(pages) == 1:
            await interaction.followup.send(embeds=[pages[0]])
        else:
            await interaction.followup.send(embeds=[pages[0]], view=view)

        view.message = await interaction.original_response()
