from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from typing import Union

from .subcommands.add import addSC
from .subcommands.edit import editSC
from .subcommands.leaderboard import leaderboardSC
from .subcommands.list import listSC
from .subcommands.perms import permsSC
from .subcommands.remove import removeSC


class TK(commands.GroupCog, name="tk"):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        super().__init__()

    """
    Add to users TKs.

    Parameters:
        killer (discord.Member): Player who TK'd.
        killed (discord.Member): Player who was TK'd.
        description (str): Description of what happened.
        video (str, optional): Link to video evidence. Defaults to None.
    """

    @commands.guild_only()
    @app_commands.command(name="add", description="Add to users TKs")
    @app_commands.describe(
        killer="Player who TK'd",
        killed="Player who was TK'd",
        description="Description of what happened",
        video="Link to video evidence",
    )
    async def add(
        self,
        interaction: discord.Interaction,
        killer: discord.Member,
        killed: discord.Member,
        description: str,
        video: str = None,
    ) -> None:
        await interaction.response.defer()
        await addSC.add(interaction, killer, killed, description, video)

    """
    Edit a TK.

    Parameters:
        id (int): ID of TK from Killers list.
        category (str): Change a Team Kills Description or video link.
        value (str): What to change it to.
    """

    @commands.guild_only()
    @app_commands.command(name="edit", description="Edit a TK")
    @app_commands.describe(
        id="ID of TK from Killers list",
        category="Change a Team Kills Description or video link",
        value="What to change it to",
    )
    @app_commands.choices(
        category=[
            Choice(name="Description", value="description"),
            Choice(name="Video Link", value="video_link"),
        ]
    )
    async def edit(
        self, interaction: discord.Interaction, id: int, category: str, value: str
    ) -> None:
        await interaction.response.defer()
        await editSC.edit(interaction, id, category, value)

    """
    A command that displays the TK leaderboard in the current guild.
    """

    @commands.guild_only()
    @app_commands.command(name="leaderboard", description="See the TK leaderboard")
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        await leaderboardSC.leaderboard(interaction)

    """
    List a user's TKs.

    Args:
        killer (discord.Member): The player who TK'd.
    """

    @commands.guild_only()
    @app_commands.command(name="list", description="List a users TKs")
    @app_commands.describe(killer="Player who TK'd")
    async def list(
        self, interaction: discord.Interaction, killer: discord.Member
    ) -> None:
        await interaction.response.defer()
        await listSC.list(interaction, killer)

    """
    Change permissions from a specific user/role.

    Parameters:
        target (Union[discord.Member, discord.Role], optional): The user or role to modify permissions for. Defaults to None.
    """

    @commands.guild_only()
    @app_commands.command(
        name="perms",
        description="List/Add/Remove permissions from a specific user/role",
    )
    @app_commands.describe(target="A User/Role to modify")
    async def perms(
        self,
        interaction: discord.Interaction,
        target: Union[discord.Member, discord.Role] = None,
    ) -> None:
        await interaction.response.defer()
        await permsSC.perms(interaction, target)

    """
    Removes a user's TK entry from the database.

    Args:
        id (int): The ID of the TK entry to remove.
    """

    @commands.guild_only()
    @app_commands.command(name="remove", description="remove a users TKs")
    @app_commands.describe(id="ID of the TK to remove")
    async def remove(self, interaction: discord.Interaction, id: int) -> None:
        await interaction.response.defer()
        await removeSC.remove(interaction, id)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(TK(bot))
