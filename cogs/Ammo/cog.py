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

    @app_commands.command(name="ammo", description="Displays ammo information")
    @app_commands.describe(caliber="Ammo Type", sort="Sort by", hidden="Hide message?")
    @app_commands.choices(caliber=calibers, sort=sort)
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
        ammos = json.loads(
            json.dumps([ammo for ammo in ammoJson if ammo["Caliber"] == caliber])
        )

        for ammo in ammos:
            ammoName: str = (
                (" ".join(ammo["Name"].split(" ")[1:]))
                .replace("Blackout", "")
                .replace(" slug", "")
                .replace(" buckshot", "")
                .replace(" Premier HP", "")
                .replace('"', "")
                .replace(" armor-piercing", "")
                .replace("makeshift ", "")
                .replace(" flashbang round", "")
                .replace("Lapua Magnum ", "")
                .replace("distress signal ", "")
                .replace("cartridge", "cart.")
            )
            ammoList.append(
                {
                    "name": ammoName,
                    "pen": int(ammo["Penetration Power"]),
                    "damage": int(ammo["Flesh Damage"]),
                    "frag": int(float(ammo["Frag Chance"]) * 100),
                    "recoil": int(ammo["Recoil"]),
                }
            )

        ammoSorted = sorted(ammoList, key=lambda e: e[sort], reverse=True)
        for ammo in ammoSorted:
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
        t2ascii = table2ascii(
            header=header, body=body, style=PresetStyle.thin_double_rounded
        )

        embed: Embed = await EB(
            title=f"{conf['ammo'][caliber]['base']} Ammo Chart",
            title_url=conf["ammo"][caliber]["wiki"],
            description=f"[Ammo Ballistics Chart]({conf['ammo_ballistics']})```{t2ascii}```\n",
        )

        await interaction.followup.send(embed=embed, ephemeral=hidden)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Ammo(bot))
