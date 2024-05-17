import discord
import json
from discord import Embed
from discord.ui import Button
from .goons import GoonsButton
from .cult import CultButton
from utils.embedbuilder import embedbuilder as EB

VIEW_NAME = "MapView"


class MapView(discord.ui.View):
    def __init__(self, origMap, conf):
        super().__init__(timeout=None)

        with open("./configs/data/bosses.json", "r") as f:
            bossJson = json.load(f)

        cult = False
        goons = False

        for boss in bossJson:
            if boss["Map"] == origMap or (
                boss["Map"] == "Sandbox" and origMap == "Ground Zero"
            ):
                if boss["BossName"] == "sectantPriest":
                    cult = True
                    continue
                if boss["BossName"] == "bossKnight":
                    goons = True
                    continue

        if "interactive" in conf["locations"][origMap]:
            self.add_item(
                Button(
                    label="Interactive Map",
                    url=conf["locations"][origMap]["interactive"],
                )
            )

        for maps in conf["locations"][origMap]:
            if (
                maps != "duration"
                and maps != "players"
                and maps != "base"
                and maps != "interactive"
                and maps != "internal"
            ):
                self.add_item(MapButton(origMap, maps, conf))

        if goons:
            self.add_item(GoonsButton(origMap, maps, conf))

        if cult:
            self.add_item(CultButton(origMap, maps, conf))

    async def on_timeout(self):
        self.clear_items()


class MapButton(discord.ui.Button):
    def __init__(self, origMap, map, conf):
        self.origMap = origMap
        self.map = map
        self.conf = conf
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="2D Map" if map == "map" else map.capitalize(),
            custom_id=map,
        )

    async def callback(self, interaction: discord.Interaction):
        author = (
            "2D Map"
            if self.custom_id == "map"
            else f"{self.custom_id.capitalize()} Map"
        )
        img = f"{self.conf['locations'][self.origMap][self.custom_id]}/revision/latest/scale-to-width-down/1000"
        await interaction.response.defer(ephemeral=True)
        embed: Embed = await EB(
            author=author,
            description=f"[**Hi-res Here**]({self.conf['locations'][self.origMap][self.custom_id]})",
            image_url=img,
        )

        await interaction.followup.send(embed=embed, ephemeral=True)
