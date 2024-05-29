import discord
import json
import utils.db as db
from discord import Embed
from utils.embedbuilder import embedbuilder as EB
import logging

logger = logging.getLogger("discord")


async def checkperms(interaction: discord.Interaction, command):
    user: discord.Member = interaction.user

    # User is Guild owner or MummyX
    if interaction.guild.owner_id == user.id or user.id == 170925319518158848:
        return True

    query = f"SELECT perms FROM tk_bot.perms WHERE guild_id = {interaction.guild.id}"
    result = (await db.fetch(query))[0]["perms"]

    if isinstance(result, dict):
        result = json.dumps(result)

    result = json.loads(result)

    for role in user.roles:
        if result.get(str(role.id)):
            logger.debug("Found permissions role")
            logger.debug(result[str(role.id)][command])
            if result[str(role.id)][command]:
                return True

    if result.get(user.id):
        logger.debug("Found permissions user")
        logger.debug(result[str(user.id)][command])
        if result[str(user.id)][command]:
            return True

    embed: Embed = EB(
        title="Insufficient Permissions",
        description=f"You do not have access to use this **/TK {command}**, by default the owner of the server must give out permissions.",
    )
    await interaction.followup.send(embed=embed)

    return False
