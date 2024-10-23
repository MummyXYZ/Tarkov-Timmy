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


class addSC:
    async def add(
        interaction: discord.Interaction,
        killer: discord.Member,
        killed: discord.Member,
        description: str,
        video: str = None,
    ) -> None:
        await interaction.response.defer()

        # Permission Check
        if not await CP(interaction, "add"):
            return

        # Validate video URL if provided
        if video and not validators.url(video):
            embed: Embed = EB(
                title="Input Error", description="Invalid URL, please try again."
            )
            await interaction.followup.send(embed=embed)
            return

        guild = interaction.guild

        # Get the Guild Icon URL
        guild_icon_url = guild.icon.url if guild.icon else None

        # Get the Guild Member Count
        guild_member_count = guild.member_count

        # Get the Killer's Avatar URL
        killer_avatar_url = killer.avatar.url if killer.avatar else killer.default_avatar.url

        # Get the Killed's Avatar URL
        killed_avatar_url = killed.avatar.url if killed.avatar else killed.default_avatar.url

        try:
            # Perform all queries within a single transaction
            async with db.pool.acquire() as cxn:
                async with cxn.transaction():
                    # Get the latest ID from the database and increment it
                    query = "SELECT id FROM tk_bot.entries WHERE guild_id = $1 ORDER BY id DESC LIMIT 1"
                    params = (guild.id,)
                    latest_entry = await cxn.fetch(query, *params)

                    # Increment ID or set to 1 if no entries exist
                    new_id = 1 if not latest_entry else latest_entry[0][0] + 1

                    # Update the Guild's name, icon URL, and member count in the 'guilds' table
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

                    # Update the Killer's name and avatar URL in the 'players' table
                    query = """
                        INSERT INTO tk_bot.players (player_id, player_name, player_icon)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (player_id) DO UPDATE SET player_name = EXCLUDED.player_name, player_icon = EXCLUDED.player_icon
                    """
                    params = (killer.id, killer.name, killer_avatar_url)
                    await cxn.execute(query, *params)

                    # Update the Killed's name and avatar URL in the 'players' table
                    query = """
                        INSERT INTO tk_bot.players (player_id, player_name, player_icon)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (player_id) DO UPDATE SET player_name = EXCLUDED.player_name, player_icon = EXCLUDED.player_icon
                    """
                    params = (killed.id, killed.name, killed_avatar_url)
                    await cxn.execute(query, *params)

                    # Prepare the query based on whether a video is provided
                    if video:
                        query = """
                            INSERT INTO tk_bot.entries (id, guild_id, killer_id, killed_id, date, description, video_link)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            RETURNING id
                        """
                        params = (
                            new_id,
                            guild.id,
                            killer.id,
                            killed.id,
                            datetime.now(),
                            description,
                            video,
                        )
                    else:
                        query = """
                            INSERT INTO tk_bot.entries (id, guild_id, killer_id, killed_id, date, description)
                            VALUES ($1, $2, $3, $4, $5, $6)
                            RETURNING id
                        """
                        params = (
                            new_id,
                            guild.id,
                            killer.id,
                            killed.id,
                            datetime.now(),
                            description,
                        )

                    # Insert the new entry and retrieve the ID
                    inserted_entry = await cxn.fetch(query, *params)
                    entry_id = inserted_entry[0]["id"]

            # Build the embed description
            if video:
                desc = f"**ID: {entry_id}** - <@{killer.id}> has killed <@{killed.id}>. Here is what happened...\n[**{description}**]({video})"
            else:
                desc = f"**ID: {entry_id}** - <@{killer.id}> has killed <@{killed.id}>. Here is what happened...\n**{description}**"

            embed: Embed = EB(
                title="Team Kill Added",
                description=desc,
                timestamp=True,
                footer="If you didn't know you can add video links too!",
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error adding team kill entry: {e}")
            await interaction.followup.send("An error occurred while adding the entry.")
