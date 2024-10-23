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

    query = "SELECT perms FROM tk_bot.perms WHERE guild_id = $1"
    result = (await db.fetch(query, interaction.guild.id))[0]["perms"]

    if not isinstance(result, dict):
        result: dict = json.loads(result)

    if user.roles:
        for role in user.roles:
            role_perms = result.get(str(role.id))
            if role_perms and role_perms.get(command):
                return True 
    else:
        if result[str(interaction.guild.id)][command]:
            return True

    user_perms = result.get(str(user.id))
    if user_perms and user_perms.get(command):
        return True

    embed: Embed = EB(
        title="Insufficient Permissions",
        description=f"You do not have access to use this **/TK {command}**, by default the owner of the server must give out permissions.",
    )
    await interaction.followup.send(embed=embed)

    return False
