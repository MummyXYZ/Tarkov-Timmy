from __future__ import annotations

import discord
import json
from discord import Embed, app_commands
from discord.ext import commands
from datetime import datetime
from utils.embedbuilder import embedbuilder as EB

import logging
import logging.handlers

logger = logging.getLogger("discord")

emoji = {
    "Fence": "<:Fence:1265002810790117459>",
    "Jaeger": "<:Jaeger:1265002835502829632>",
    "Mechanic": "<:Mechanic:1265002843295711387>",
    "Peacekeeper": "<:Peacekeeper:1265002852183445515>",
    "Prapor": "<:Prapor:1265002862321074186>",
    "Ragman": "<:Ragman:1265002869803847761>",
    "Ref": "<:Ref:1265002880696320040>",
    "Skier": "<:Skier:1265002889470939278>",
    "Therapist": "<:Therapist:1265002897561882756>",
}


def tradersEmbed() -> Embed:
    with open("./configs/data/traderresets.json", "r") as f:
        tradersJson = json.load(f)

    value = ""

    embed: Embed = EB(
        title="Trader Resets", footer="Information may have some inaccuracies"
    )

    for trader in tradersJson:
        if trader["name"] == "Lightkeeper" or trader["name"] == "BTR Driver":
            continue
        reset_timestamp = datetime.fromisoformat(trader["resetTime"]).timestamp()
        if datetime.now().timestamp() > reset_timestamp:
            value = "Recently reset"
        else:
            value = f"<t:{int(reset_timestamp)}:R>\n"

        embed.add_field(name=f"{emoji[trader['name']]}{trader['name']}", value=value)

    return embed


class TraderView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Refresh",
        style=discord.ButtonStyle.green,
        custom_id="trader_view:refresh",
    )
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = tradersEmbed()
        await interaction.response.edit_message(embed=embed, view=self)


class Traders(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        self.startTime = datetime.now()

    @app_commands.command(
        name="traders",
        # Short description of the command
        description="Reset timers for Traders",
        # Help description of the command
        extras=[
            """Displays reset timers for Traders with a refresh button for ease of use.
            
            **E.g.** </traders:1251904115936727142>""",
        ],
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def traders(self, interaction: discord.Interaction):
        await interaction.response.defer()

        embed = tradersEmbed()

        await interaction.followup.send(embed=embed, view=TraderView())


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Traders(bot))
    bot.add_view(TraderView())
