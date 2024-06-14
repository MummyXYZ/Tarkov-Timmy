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


@app_commands.guild_only()
@app_commands.allowed_installs(guilds=True, users=False)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
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

    @app_commands.command(
        name="add",
        # Short description of the command
        description="Add to users TKs",
        # Help description of the command
        extras=[
            """Keep track of your guilds team kills by adding them with this command.
            
            **E.g.** </tk add:1241780138593616026> <@KILLER> <@KILLED> <GL Accident> [[URL](https://youtu.be/btVxW309bEE)]
            (*<> are required, [] are optional*)""",
        ],
    )
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

    @app_commands.command(
        name="edit",
        # Short description of the command
        description="Edit a TK",
        # Help description of the command
        extras=[
            """Edit your guilds team kills.
            
            **E.g.** </tk edit:1241780138593616026> <@ID> <Description/Video> <New Value>
            (*<> are required*)""",
        ],
    )
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

    @app_commands.command(
        name="leaderboard",
        # Short description of the command
        description="See the TK leaderboard",
        # Help description of the command
        extras=[
            """Display the team kill leaders.
            
            **E.g.** </tk leaderboard:1241780138593616026>""",
        ],
    )
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        await leaderboardSC.leaderboard(interaction)

    """
    List a user's TKs.

    Args:
        killer (discord.Member): The player who TK'd.
    """

    @app_commands.command(
        name="list",
        # Short description of the command
        description="List a users TKs",
        # Help description of the command
        extras=[
            """Display a members team kills.
            
            **E.g.** </tk list:1241780138593616026> <@User>
            (*<> are required*)""",
        ],
    )
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

    @app_commands.command(
        name="perms",
        # Short description of the command
        description="List/Add/Remove permissions from a specific user/role",
        # Help description of the command
        extras=[
            """Edit or list permissions for the TK commands.
            
            **E.g.**
            To list permissions: </tk perms:1241780138593616026>
            To edit permissions: </tk perms:1241780138593616026> [@User/@Role]
            (*[] are optional*)""",
        ],
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

    @app_commands.command(
        name="remove",
        # Short description of the command
        description="remove a users TKs",
        # Help description of the command
        extras=[
            """Remove a team kill from someones list.

            To get a team kill ID use /tk list <@User>
            **E.g.** </tk remove:1241780138593616026> <@ID>
            (*<> are required*)""",
        ],
    )
    @app_commands.describe(id="ID of the TK to remove")
    async def remove(self, interaction: discord.Interaction, id: int) -> None:
        await interaction.response.defer()
        await removeSC.remove(interaction, id)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(TK(bot))
