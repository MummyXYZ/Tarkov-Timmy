from __future__ import annotations

import discord
import json
import requests
from discord import Embed
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from bs4 import BeautifulSoup as soup
from .map_view import MapView
from utils.embedbuilder import embedbuilder as EB


class Map(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    maps = []
    with open("./configs/conf.json", "r") as f:
        conf = json.load(f)

    with open("./configs/data/maps.json", "r") as f:
        mapsJson = json.load(f)

    for location in conf["locations"]:
        loc_Data = conf["locations"][location]
        for y in mapsJson:
            if y["Map Internal Name"] == loc_Data["internal"] and not y["Map Locked"]:
                maps.append(Choice(name=location.title(), value=location))

    @app_commands.command(
        name="map", description="Maps and information for a specific location"
    )
    @app_commands.describe(map="Specify the map", hidden="Hide message?")
    @app_commands.choices(map=maps)
    async def map(
        self, interaction: discord.Interaction, map: str, hidden: bool = True
    ):
        await interaction.response.defer(ephemeral=hidden)

        with open("./configs/conf.json", "r") as f:
            conf = json.load(f)

        with open("./configs/data/maps.json", "r") as f:
            mapsJson = json.load(f)

        with open("./configs/data/bosses.json", "r") as f:
            bossJson = json.load(f)

        url = "https://escapefromtarkov.fandom.com/wiki/{0}".format(
            map.title().replace(" ", "_").replace("Of", "of")
        )
        res = requests.get(url)
        mapWiki = soup(res.text, "html.parser")

        for mapData in mapsJson:
            if mapData["Map Internal Name"] == conf["locations"][map]["internal"]:
                duration = f"{mapData['Raid Timer']} Mins"
                players = (
                    f"{int(mapData['Min Players'])} - {int(mapData['Max Players'])}"
                )

        flavor = f"{mapWiki.find(id='Description').find_next('p').text}"
        image = (
            f"{conf['locations'][map]['base']}/revision/latest/scale-to-width-down/800"
        )
        description = ""

        # Boss Variables
        bossName: str = None
        bossChance: str = None
        bossEscorts: str = None

        cult: bool = False
        goons: bool = False

        for boss in bossJson:
            if boss["MAP_ID"] == conf["locations"][map]["internal"]:
                if boss["BossName"] == "sectantPriest":
                    cult = True
                    continue
                if boss["BossName"] == "bossKnight":
                    goons = True
                    continue
                if (
                    boss["BossName"] == "bossTagilla"
                    and boss["MAP_ID"] == "factory4_night"
                ):
                    continue
                if (
                    boss["BossName"] == "pmcBot"
                    or boss["BossName"] == "exUsec"
                    or boss["BossName"] == "gifter"
                    or boss["BossName"] == "bossBoarSniper"
                ):
                    continue

                nameTemp = boss["BossName"].removeprefix("boss")
                if nameTemp == "Bully":
                    nameTemp = "Reshala"
                if nameTemp == "Kojaniy":
                    nameTemp = "Shturman"
                if nameTemp == "Boar":
                    nameTemp = "Kaban"
                if bossName is None:
                    bossName = f"[{nameTemp}](https://escapefromtarkov.fandom.com/wiki/{nameTemp})"
                    bossChance = f"{boss['BossChance']}%"
                    bossEscorts = f"{boss['BossEscortAmount']}"
                else:
                    if nameTemp != "Kolontay":
                        bossName += f", [{nameTemp}](https://escapefromtarkov.fandom.com/wiki/{nameTemp})"
                        bossChance += f", {boss['BossChance']}%"
                        bossEscorts += f", {boss['BossEscortAmount']}"

        if bossName:
            description = f"**Boss:** {bossName}\n**Spawn Chance:** {bossChance}\n**Followers:** {bossEscorts}"

        embed: Embed = EB(
            title=map,
            title_url=url,
            description=description,
            image_url=image,
            footer=flavor,
        )

        embed.add_field(inline=True, name="Duration", value=duration)
        embed.add_field(inline=True, name="Players", value=players)
        embed.add_field(inline=True, name="The Goons", value=True if goons else False)
        embed.add_field(inline=True, name="Cultists", value=True if cult else False)

        await interaction.followup.send(
            embed=embed, view=MapView(map, conf), ephemeral=True
        )


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Map(bot))
