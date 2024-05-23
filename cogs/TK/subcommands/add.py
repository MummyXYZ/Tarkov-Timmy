import discord
import validators
import utils.db as db
from discord import Embed
from datetime import datetime, timezone
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
        # Permission Check
        if not await CP(interaction, "add"):
            return
            # Validate URL for embeding Ex.(✅: "https://google.com" ❌: google.com)
        if video:
            if not validators.url(video):
                embed: Embed = EB(
                    title="Input Error", description="Invalid URL, please try again."
                )
                await interaction.followup.send(embed=embed)
                return

        guild = interaction.guild
        desc = ""

        query = "SELECT id FROM tk_bot.entries WHERE guild_id = %s ORDER BY date ASC "
        params = (guild.id,)
        res = db.execute(query, params)

        if not res:
            id = 1
        else:
            id = res[-1][0] + 1

        if not video:
            query = "INSERT INTO tk_bot.entries (id, guild_id, killer_id, killed_id, date, description) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"
            params = (
                id,
                guild.id,
                killer.id,
                killed.id,
                datetime.now(timezone.utc),
                description,
            )
        else:
            query = "INSERT INTO tk_bot.entries (id, guild_id, killer_id, killed_id, date, description, video_link) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id"
            params = (
                id,
                guild.id,
                killer.id,
                killed.id,
                datetime.now(timezone.utc),
                description,
                video,
            )
        res = db.execute(query, params)

        if not video:
            desc = f"**ID: {id}** - <@{killer.id}> has killed <@{killed.id}>. Here is what happened...\n**{description}**"
        else:
            desc += f"**ID: {id}** - <@{killer.id}> has killed <@{killed.id}>. Here is what happened...\n[**{description}**]({video})"
        embed: Embed = EB(title="Team Kill Added", description=desc, timestamp=True)

        await interaction.followup.send(embed=embed)
