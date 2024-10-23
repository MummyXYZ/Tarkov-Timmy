from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

def inGameTime(left) -> str:
    utc_Time = datetime.now(timezone.utc).timestamp()
    leftOffset = timedelta(hours=0) if left else timedelta(hours=12)
    russiaOffset = timedelta(hours=7)
    tarkyMultiplier = 7
    tarkyTime = (
        datetime.fromtimestamp(((utc_Time * tarkyMultiplier) % 86400000))
        + russiaOffset
        + leftOffset
    )
    tarkyTimeF = tarkyTime.strftime("%H:%M:%S")
    return tarkyTimeF

class TimeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            TimeButton(
                custom_id="time_button",
                label=f"{inGameTime(True)} ⌚ {inGameTime(False)}",
            )
        )

    async def on_timeout(self):
        self.clear_items()

class TimeButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        try: 
            self.label = f"{inGameTime(True)} ⌚ {inGameTime(False)}"
            await interaction.response.edit_message(view=self.view)
        except Exception as e:
            print(f"Error updating time button: {e}")


class Time(commands.Cog, name="time"):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @app_commands.command(
        name="time",
        # Short description of the command
        description="Current in-game raid time",
        # Help description of the command
        extras=[
            """Displays a button that has in-game Tarkov time. Press the button to refresh the time.
            
            **E.g.** </time:1241780138593616022>""",
        ],
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def time(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(view=TimeView())


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Time(bot))
    bot.add_view(TimeView())
