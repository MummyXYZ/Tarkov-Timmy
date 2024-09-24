from __future__ import annotations

import discord
import json
from discord import Embed
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from table2ascii import PresetStyle, table2ascii
from utils.embedbuilder import embedbuilder as EB


class Ammo(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    calibers = []
    with open("./configs/conf.json", "r") as f:
        conf = json.load(f)

    for x, val in conf["ammo"].items():
        calibers.append(Choice(name=val["base"], value=x))

    sort = [
        Choice(name="Penetration", value="pen"),
        Choice(name="Damage", value="damage"),
        Choice(name="Fragmentation Chance", value="frag"),
        Choice(name="Recoil", value="recoil"),
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
    @app_commands.choices(caliber=calibers, sort=sort)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ammo(
        self,
        interaction: discord.Interaction,
        caliber: str,
        sort: str = "pen",
        hidden: bool = True,
    ):
        await interaction.response.defer(ephemeral=hidden)

        with open("./configs/conf.json", "r") as f:
            conf = json.load(f)

        with open("./configs/data/ammunitions.json", "r") as f:
            ammoJson = json.load(f)

        body, ammoList = [], []
        # Extract the ammunition data for the specified caliber
        ammos = json.loads(
            json.dumps([ammo for ammo in ammoJson if ammo["caliber"] == caliber])
        )

        for ammo in ammos:
            ammoName = ammo["item"]["shortName"]
            ammoList.append(
                {
                    "name": ammoName,
                    "pen": int(ammo["penetrationPower"]),
                    "damage": int(ammo["damage"]),
                    "frag": int(ammo["fragmentationChance"]) * 100,
                    "recoil": int(ammo["recoilModifier"] * 100),
                    "projCount": int(ammo["projectileCount"]),
                }
            )

        # Sort the ammoList by the specified sort criteria
        ammoSorted = sorted(ammoList, key=lambda e: e[sort], reverse=True)
        for ammo in ammoSorted:
            if ammo["projCount"] > 1:
                ammo["damage"] = f"{ammo['damage']}x{ammo['projCount']}"
            body.append(
                [
                    ammo["name"],
                    ammo["pen"],
                    ammo["damage"],
                    f"{ammo['frag']}%",
                    f"{ammo['recoil']}",
                ]
            )

        header = ["", "PEN", "DMG", "FRAG%", "RECOIL"]
        # Generate the table using table2ascii
        t2ascii = table2ascii(
            header=header, body=body, style=PresetStyle.double_thin_box
        )

        # Create the embed with the table
        embed: Embed = EB(
            title=f"{conf['ammo'][caliber]['base']} Ammo Chart",
            title_url=conf["ammo"][caliber]["wiki"],
            description=f"[Ammo Ballistics Chart]({conf['ammo_ballistics']})```{t2ascii}```\n",
        )

        await interaction.followup.send(embed=embed, ephemeral=hidden)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Ammo(bot))
