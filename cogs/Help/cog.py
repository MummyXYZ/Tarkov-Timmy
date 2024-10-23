from __future__ import annotations

import discord
from discord import Embed, app_commands
from discord.ext import commands
from typing import Optional, List
from utils.embedbuilder import embedbuilder as EB


class HelpDropdown(discord.ui.Select):
    def __init__(self, bot: commands.AutoShardedBot, options: List[discord.SelectOption]):
        self.bot = bot
        super().__init__(
            placeholder="Select a command",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        # Find the selected command more efficiently using a dict lookup
        selected_command = next(
            (app for app in self.bot.tree.walk_commands()
             if app.qualified_name.title() == self.values[0]),
            None
        )

        # Handle case if command is not found (shouldn't happen)
        if selected_command:
            description = selected_command.extras[0] if selected_command.extras else "No description provided"
            embed = EB(
                title=selected_command.qualified_name.title(),
                description=description
            )
        else:
            embed = EB(
                title="Command not found",
                description="The selected command could not be found."
            )

        await interaction.response.edit_message(embed=embed)


class SlashHelpView(discord.ui.View):
    def __init__(self, bot: commands.AutoShardedBot, options: List[discord.SelectOption], *, timeout: Optional[float] = 120.0):
        super().__init__(timeout=timeout)
        self.add_item(HelpDropdown(bot, options))


class Help(commands.Cog, name="Help"):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        description="Help for the various commands of the TK Bot",
        extras=[
            """Provides examples of commands and other useful information.
            
            **E.g.** </help:1241780138593616024>""",
        ],
    )
    @app_commands.describe(hidden="Hide message?")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def help(self, interaction: discord.Interaction, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        # Create initial help embed
        embed = EB(
            title="Help",
            description="Please select one of the commands below to receive more information and examples.",
        )

        # Fetch the available command options
        options = await self._get_command_options()
        await interaction.followup.send(
            embed=embed,
            view=SlashHelpView(self.bot, options),
            ephemeral=hidden,
        )

    async def _get_command_options(self) -> List[discord.SelectOption]:
        """Fetch and sort the commands into options for the dropdown."""
        commands_list = sorted(
            (app for app in self.bot.tree.walk_commands()
             if not hasattr(app, "_children")),
            key=lambda app: app.qualified_name
        )

        options = [
            discord.SelectOption(
                label=app.qualified_name.title(),
                description=(app.description[:100]
                             if app.description else None)
            )
            for app in commands_list
        ]

        return options


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Help(bot))
