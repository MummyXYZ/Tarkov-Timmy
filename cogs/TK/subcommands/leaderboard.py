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
        desc = ""

        query = f"SELECT killer_id, COUNT(killer_id) AS count FROM tk_bot.entries WHERE guild_id='{guild.id}' GROUP BY killer_id ORDER BY count DESC"
        result = await db.fetch(query)
        descs, pages = [], []
        if not result:
            descs.append("No TKs on this server.")
        else:
            for count, x in enumerate(result, 0):
                if count % 10 == 0:
                    descs.append(f"<@{x[0]}> - **{x[1]}**")
                    continue

                if len(result) != count and count % 10 != 0:
                    descs[-1] += "\n"

                descs[-1] += f"<@{x[0]}> - **{x[1]}**"

        for desc in descs:
            pages.append(EB(title=f"{guild.name} Leaderboard", description=f"{desc}"))

        view = ButtonMenu(pages, 120)
        if len(pages) == 1:
            await interaction.followup.send(
                embeds=pages[0] if isinstance(pages[0], list) else [pages[0]]
            )
        else:
            await interaction.followup.send(
                embeds=pages[0] if isinstance(pages[0], list) else [pages[0]],
                view=view,
            )
        view.message = await interaction.original_response()
