from __future__ import annotations

import discord
import json
from itertools import cycle
from datetime import datetime, timedelta
from discord import app_commands, Embed
from discord.ext import commands
from utils.embedbuilder import embedbuilder as EB

images = cycle(["big_pipe.png", "birdeye.png", "knight.png"])


def goonsEmbed():
    with open("./configs/data/goons.json", "r") as f:
        conf = json.load(f)

    timestamp = int(
        (
            datetime.strptime(conf["Time"][0], "%B %d, %Y, %I:%M %p")
            + timedelta(hours=1)
        ).timestamp()
    )

    file = discord.File("./assets/" + next(images), filename="image.png")

    embed: Embed = EB(
        title="Goons Sightings",
        description="The most recent Goons sighting.",
        thumbnail="attachment://image.png",
        footer="Powered by TarkovPal.com",
        footer_icon="https://tarkovpal.com/logov2.png",
    )

    embed.add_field(
        name="Map",
        value=conf["Current Map"][0],
    )
    embed.add_field(name="Last Seen", value=f"<t:{timestamp}:t>")

    return (embed, file)


class GoonsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Refresh",
        style=discord.ButtonStyle.green,
        custom_id="goons_view:refresh",
    )
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed, file = goonsEmbed()
        await interaction.response.edit_message(embed=embed, view=self)


class Goons(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @app_commands.command(
        name="goons",
        # Short description of the command
        description="Displays information about what map The Goons are on",
        # Help description of the command
        extras=[
            """Display community provided information of where the Goons may be spawning.
            
            **E.g.** </goons:1245395766374170644>""",
        ],
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def map(self, interaction: discord.Interaction):
        await interaction.response.defer()

        embed, file = goonsEmbed()
        await interaction.followup.send(embed=embed, file=file, view=GoonsView())


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Goons(bot))
