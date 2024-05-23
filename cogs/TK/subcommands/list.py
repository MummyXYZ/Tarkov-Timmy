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
        #     # Permission Check
        if not await CP(interaction, "list"):
            return

        guild = interaction.guild
        desc = ""

        query = "SELECT id, killer_id, killed_id, description, date, video_link FROM tk_bot.entries WHERE guild_id = %s AND killer_id = %s ORDER BY date ASC "
        params = (guild.id, killer.id)

        result = db.execute(query, params)

        descs, pages = [], []
        if not result:
            descs.append("No TKs on this server.")
        else:
            for count, x in enumerate(result, 0):
                utc_time = int(x[4].astimezone(timezone.utc).timestamp())
                # utc_time = calendar.timegm(x[4].timetuple())
                if count % 10 == 0:
                    if x[5]:
                        descs.append(
                            f"<@{killer.id}>**'s kills - {len(result)}**\n\n**ID: {x[0]}** - <@{x[1]}> killed <@{x[2]}>\n[**{x[3]}**]({x[5]}) - <t:{utc_time}:R>"
                        )
                    else:
                        descs.append(
                            f"<@{killer.id}>**'s kills - {len(result)}**\n\n**ID: {x[0]}** - <@{x[1]}> killed <@{x[2]}>\n**{x[3]}** - <t:{utc_time}:R>"
                        )
                    continue
                if len(result) != count and count % 10 != 0:
                    descs[-1] += "\n\n"

                if x[5]:
                    descs[-1] += (
                        f"**ID: {x[0]}** - <@{x[1]}> killed <@{x[2]}>\n[**{x[3]}**]({x[5]}) - <t:{utc_time}:R>"
                    )
                else:
                    descs[-1] += (
                        f"**ID: {x[0]}** - <@{x[1]}> killed <@{x[2]}>\n**{x[3]}** - <t:{utc_time}:R>"
                    )

        for desc in descs:
            pages.append(EB(description=f"{desc}"))

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
