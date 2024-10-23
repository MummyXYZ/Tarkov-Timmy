from __future__ import annotations

import discord
import json
from typing import List
from discord import app_commands
from discord.ext import commands
from table2ascii import PresetStyle, table2ascii
from utils.embedbuilder import embedbuilder as EB

class Ammo(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        # Load calibers and ballistics chart link from conf.json
        with open("./configs/conf.json", "r") as f:
            config = json.load(f)
            # Sort calibers alphabetically by their base name
            self.calibers = dict(sorted(config["ammo"].items(), key=lambda x: x[1]["base"]))
            self.ballistics_chart = config["ammo_ballistics"]  # Ballistics chart link

        # Define the sorting choices
        self.sort_criteria = [
            app_commands.Choice(name="Penetration", value="penetrationPower"),
            app_commands.Choice(name="Damage", value="damage"),
            app_commands.Choice(name="Fragmentation Chance", value="fragmentationChance"),
            app_commands.Choice(name="Recoil", value="recoilModifier"),
        ]

    @app_commands.command(
        name="ammo",
        # Short description of the command
        description="Displays ammo information",
        # Help description of the command
        extras=[
            """Displays ammo information from the fandom page. The information by default is sorted by Penetration values.
            
            **E.g.**  </ammo:1260719258481066044> <7.62x39mm> [Penetration]
            (*<> are required, [] are optional*)""",
        ],
    )
    @app_commands.describe(caliber="Ammo Type", sort="Sort by", hidden="Hide message?")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ammo(
        self,
        interaction: discord.Interaction,
        caliber: str,
        sort: str = "penetrationPower",
        hidden: bool = True,  # Hidden parameter added here
    ):
        await interaction.response.defer(ephemeral=hidden)

        # Load ammo data
        with open("./configs/data/ammunitions.json", "r") as f:
            ammoJson = json.load(f)

        # Filter ammunitions based on selected caliber
        ammos = [ammo for ammo in ammoJson if ammo["caliber"] == caliber]
        if not ammos:
            await interaction.followup.send(f"No data found for {caliber}", ephemeral=True)
            return

        # Prepare the ammo data for sorting and table display
        ammo_list = [
            {
                "name": ammo["item"]["shortName"],
                "penetrationPower": int(ammo["penetrationPower"]),
                "damage": int(ammo["damage"]),
                "fragmentationChance": int(ammo["fragmentationChance"] * 100),
                "recoilModifier": int(ammo["recoilModifier"] * 100),
                "projectileCount": int(ammo["projectileCount"]),
            }
            for ammo in ammos
        ]

        # Sort the ammo list by the chosen sort parameter
        ammo_sorted = sorted(ammo_list, key=lambda x: x[sort], reverse=True)

        body = [
            [
                ammo['name'],
                ammo["penetrationPower"],
                f"{ammo['damage']}x{ammo['projectileCount']}" if ammo["projectileCount"] > 1 else ammo["damage"],
                f"{ammo['fragmentationChance']}%",
                f"{ammo['recoilModifier']}",
            ]
            for ammo in ammo_sorted
        ]

        header = ["", "PEN", "DMG", "FRAG%", "RECOIL"]

        t2ascii = table2ascii(
            header=header,
            body=body,
            style=PresetStyle.double_thin_box
        )

        embed = EB(
            title=f"{self.calibers[caliber]['base']} Ammo Chart",
            title_url=self.calibers[caliber]["wiki"],
            description=f"[Ammo Ballistics Chart]({self.ballistics_chart})\n```{t2ascii}```",
        )

        await interaction.followup.send(embed=embed, ephemeral=hidden)

    # Autocomplete method for calibers
    @ammo.autocomplete("caliber")
    async def ammo_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        # Filter calibers based on current input
        choices = [
            app_commands.Choice(name=val["base"], value=key)
            for key, val in self.calibers.items()
            if current.lower() in val["base"].lower()
        ]
        # Return at most 25 options
        return choices[:25]

    # Autocomplete method for sort parameter
    @ammo.autocomplete("sort")
    async def sort_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        # Return sort choices that match user input
        choices = [choice for choice in self.sort_criteria if current.lower() in choice.name.lower()]
        return choices[:25]

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Ammo(bot))
