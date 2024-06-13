from __future__ import annotations

import discord
from discord import Embed, app_commands
from discord.ext import commands
from typing import Optional
from utils.embedbuilder import embedbuilder as EB


class HelpDropdown(discord.ui.Select):
    def __init__(
        self, bot: commands.AutoShardedBot, options: list[discord.SelectOption]
    ):
        self.bot = bot
        super().__init__(
            placeholder="Select a command",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selected: commands.Command = None

        for app in self.bot.tree.walk_commands():
            if hasattr(app, "_children"):
                continue
            if app.qualified_name.title() == self.values[0]:
                selected = app
                break

        embed = EB(
            title=selected.qualified_name.title(),
            description=selected.extras[0]
            if selected.extras and len(selected.extras) > 0
            else "No description provided",
        )
        await interaction.response.edit_message(embed=embed)


class SlashHelpView(discord.ui.View):
    def __init__(
        self: discord.ui.View,
        bot: commands.AutoShardedBot,
        options: list[discord.SelectOption],
        *,
        timeout: Optional[float] = 120.0,
    ):
        super().__init__(timeout=timeout)

        self.add_item(HelpDropdown(bot, options))


class Help(commands.Cog, name="Help"):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        # Short description of the command
        description="Help for the various commands of the TK Bot",
        # Help description of the command
        extras=[
            """Provides examples of commands and other useful information.
            
            **E.g.** </help:1241780138593616024>""",
        ],
    )
    @app_commands.describe(hidden="Hide message?")
    async def help(self, interaction: discord.Interaction, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)
        embed: Embed = EB(
            title="Help",
            description="Please select one of the commands below to receive more information and examples.",
        )

        options = await self._cog_select_options()
        await interaction.followup.send(
            embed=embed,
            view=SlashHelpView(self.bot, options),
            ephemeral=hidden,
        )

    async def _cog_select_options(self) -> list[discord.SelectOption]:
        options: list[discord.SelectOption] = []

        apps = sorted(self.bot.tree.walk_commands(), key=lambda app: app.qualified_name)
        for app in apps:
            if hasattr(app, "_children"):
                continue
            options.append(
                discord.SelectOption(
                    label=app.qualified_name.title() if app else "No Category",
                    description=app.description[:100] if app.description else None,
                )
            )

        return options


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Help(bot))
