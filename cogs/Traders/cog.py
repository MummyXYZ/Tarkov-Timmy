from __future__ import annotations

import discord
import json
from discord import Embed, app_commands
from discord.ext import commands, tasks
from datetime import datetime
from utils.embedbuilder import embedbuilder as EB
import logging
import logging.handlers

logger = logging.getLogger("discord")

# Trader emojis
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


class Traders(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        self.traders_data = {}
        self.load_trader_data()  # Load trader data at startup
        self.trader_cache_refresh.start()  # Start the timed cache refresh

    def load_trader_data(self) -> None:
        """Load trader data from the file."""
        try:
            with open("./configs/data/traderresets.json", "r") as f:
                self.traders_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading trader reset data: {e}")
            self.traders_data = {}  # Reset to an empty dictionary on error

    @tasks.loop(minutes=5)
    async def trader_cache_refresh(self) -> None:
        """Background task to refresh the trader data every 5 minutes."""
        self.load_trader_data()

    def traders_embed(self) -> Embed:
        """Create the embed for trader reset times using cached data."""
        embed = EB(
            title="Trader Resets",
            footer="Information may have some inaccuracies",
        )

        now = datetime.now().timestamp()

        for trader in self.traders_data:
            trader_name = trader["name"]
            if trader_name in ["Lightkeeper", "BTR Driver"]:
                continue

            reset_timestamp = datetime.fromisoformat(
                trader["resetTime"]).timestamp()
            value = "Recently reset" if now > reset_timestamp else f"<t:{int(reset_timestamp)}:R>\n"

            embed.add_field(
                name=f"{emoji.get(trader_name, '')} {trader_name}",
                value=value
            )

        return embed

    @app_commands.command(
        name="traders",
        description="Reset timers for Traders",
        extras=[
            """Displays reset timers for Traders with a refresh button for ease of use.
            
            **E.g.** </traders:1251904115936727142>""",
        ],
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def traders(self, interaction: discord.Interaction):
        await interaction.response.defer()

        embed = self.traders_embed()  # Use cached trader data
        await interaction.followup.send(embed=embed, view=TraderView(self))

    @trader_cache_refresh.before_loop
    async def before_trader_cache_refresh(self):
        """Ensure the bot is ready before starting the cache refresh loop."""
        await self.bot.wait_until_ready()


class TraderView(discord.ui.View):
    def __init__(self, cog: Traders):
        self.cog = cog  # Reference the cog to access cached data
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Refresh",
        style=discord.ButtonStyle.green,
        custom_id="trader_view:refresh",
    )
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh the trader embed using the latest cached data."""
        embed = self.cog.traders_embed()
        await interaction.response.edit_message(embed=embed, view=self)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Traders(bot))
    bot.add_view(TraderView(Traders(bot)))
