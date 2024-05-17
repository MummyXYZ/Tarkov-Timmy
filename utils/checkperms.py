import discord
import json
import utils.db as db
from discord import Embed
from utils.embedbuilder import embedbuilder as EB

import logging

logger = logging.getLogger("discord")


async def checkperms(interaction: discord.Interaction, command):
    try:
        user: discord.Member = interaction.user

        # User is Administrator or MummyX
        if user.guild_permissions.administrator or user.id == 170925319518158848:
            return True

        query = f"SELECT {command} FROM perms WHERE guild_id = {interaction.guild.id} AND (target_id = {user.id}"
        for role in user.roles:
            query += f" OR target_id = {role.id}"
        query += ")"
        result = await db.query(query)

        for x in result:
            if x[0]:
                return True

        await interaction.response.defer(ephemeral=True)
        with open("./configs/help.json", "r") as f:
            help = json.load(f)
        embed: Embed = await EB(
            title="Insufficient Permissions",
            description=f"You do not have access to use this command. If this is not correct have an administrator grant you access with this command {help['tkperms'][0]}.",
        )
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.response.defer(ephemeral=True)
        logger.error(f"Leaderboard error, {e}")
        embed: Embed = await EB(
            title="Error Occured",
            description="There has been an error. Please contact MummyX#2616.",
        )

        await interaction.followup.send(embed=embed)

    return False
