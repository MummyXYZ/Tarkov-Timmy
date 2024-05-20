import discord
import json
from discord import Embed
from utils.embedbuilder import embedbuilder as EB


class CultButton(discord.ui.Button):
    def __init__(self, origMap, map, conf):
        self.origMap = origMap
        self.map = map
        self.conf = conf
        super().__init__(
            style=discord.ButtonStyle.danger, label="Cultists", custom_id="cult", row=1
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        with open("./configs/data/bosses.json", "r") as f:
            bossJson = json.load(f)

        description = "**Spawn chance:**\n"
        maps = []

        for boss in bossJson:
            if boss["BossName"] == "sectantPriest":
                if boss["Map"] in maps:
                    continue
                maps.append(boss["Map"])
                description += f"**{boss['Map'] if boss['Map'] != 'Sandbox' else 'Ground Zero'}**: {boss['BossChance']}%\n"

        embed: Embed = EB(
            title="Cultists",
            description=description,
            title_url=self.conf["cultists"]["wiki"],
            image_url=self.conf["cultists"]["img"],
        )

        await interaction.followup.send(
            embed=embed, view=CultView(self.conf), ephemeral=True
        )


class CultView(discord.ui.View):
    def __init__(self, conf):
        super().__init__(timeout=None)

        for map in conf["cultists"]["maps"]:
            self.add_item(
                CultSubButton(conf, label=f"{map.capitalize()} Map", custom_id=map)
            )

    async def on_timeout(self):
        self.clear_items()


class CultSubButton(discord.ui.Button):
    def __init__(self, conf, label, custom_id):
        self.conf = conf
        super().__init__(label=label, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        img = f"{self.conf['cultists']['maps'][self.custom_id]}/revision/latest/scale-to-width-down/800"
        desc = f"[**Hi-res Here**]({self.conf['cultists']['maps'][self.custom_id]})"
        embed: Embed = EB(
            title=f"Cultists - {self.custom_id.capitalize()}",
            description=desc,
            image_url=img,
        )

        await interaction.followup.send(embed=embed, ephemeral=True)
