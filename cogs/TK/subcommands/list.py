from __future__ import annotations

import discord
from datetime import timezone
import utils.db as db
from utils.ButtonMenu import ButtonMenu
from utils.checkperms import checkperms as CP
from utils.embedbuilder import embedbuilder as EB
import logging
import logging.handlers

logger = logging.getLogger("discord")


class listSC:
    async def list(interaction: discord.Interaction, killer: discord.Member) -> None:
        await interaction.response.defer()

        # Permission Check
        if not await CP(interaction, "list"):
            return

        guild = interaction.guild

        # Fetch Guild Icon, Member Count, and Player Avatar URLs
        guild_icon_url = guild.icon.url if guild.icon else None
        guild_member_count = guild.member_count
        killer_avatar_url = killer.avatar.url if killer.avatar else killer.default_avatar.url

        # Update the guild and player info in the database
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

                    # Update the Killer's information in the 'players' table
                    query = """
                        INSERT INTO tk_bot.players (player_id, player_name, player_icon)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (player_id) DO UPDATE 
                        SET player_name = EXCLUDED.player_name, 
                            player_icon = EXCLUDED.player_icon
                    """
                    params = (killer.id, killer.name, killer_avatar_url)
                    await cxn.execute(query, *params)

                    # SQL query to fetch entries related to the killer
                    query = """
                        SELECT id, killer_id, killed_id, description, date, video_link
                        FROM tk_bot.entries
                        WHERE guild_id = $1 AND killer_id = $2
                        ORDER BY date ASC
                    """
                    params = (guild.id, killer.id)
                    result = await cxn.fetch(query, *params)

        except Exception as e:
            logger.error(f"Error updating guild/player data: {e}")
            await interaction.followup.send("An error occurred while updating the data.")

        # Prepare description and embed pages
        descs, pages = [], []
        if not result:
            descs.append("No TKs on this server.")
        else:
            page_content = []
            for count, entry in enumerate(result, 1):
                utc_time = int(entry[4].astimezone(timezone.utc).timestamp())
                video_link = f"[**{entry[3]}**]({entry[5]})" if entry[5] else f"**{entry[3]}**"

                # Add initial header on the first entry of each page
                if count % 10 == 1:
                    page_content.append(
                        f"<@{killer.id}>**'s kills - {len(result)}**")

                # Add each entry to the page content
                page_content.append(f"**ID: {entry[0]}** - <@{entry[1]}> killed <@{entry[2]}>\n{video_link} - <t:{utc_time}:R>")

                # Every 10 items or when reaching the last item, finalize the page
                if count % 10 == 0 or count == len(result):
                    descs.append("\n\n".join(page_content))
                    page_content = []

        # Build the embed pages from the descriptions
        for desc in descs:
            pages.append(EB(description=f"{desc}"))

        view = ButtonMenu(pages, 120)

        # Send the first page with or without the view (pagination)
        if len(pages) == 1:
            await interaction.followup.send(embeds=[pages[0]])
        else:
            await interaction.followup.send(embeds=[pages[0]], view=view)

        view.message = await interaction.original_response()
