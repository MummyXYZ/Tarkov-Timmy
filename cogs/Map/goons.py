import discord
import json
from discord import Embed
from utils.embedbuilder import embedbuilder as EB


class GoonsButton(discord.ui.Button):
    def __init__(self, origMap, map, conf):
        self.origMap = origMap
        self.map = map
        self.conf = conf
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="The Goons",
            custom_id="goons",
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        with open("./configs/data/bosses.json", "r") as f:
            bossJson = json.load(f)

        description = "**Spawn chance:**\n"

        for boss in bossJson:
            if boss["BossName"] == "bossKnight":
                description += f"**{boss['Map']}**: {boss['BossChance']}%\n"

        embed = EB(
            title="The Goons",
            description=description,
            title_url=self.conf["thegoons"]["wiki"],
            image_url=self.conf["thegoons"]["img"],
        )

        embed.add_field(
            inline=True,
            name="\u200b",
            value=f"[**Big Pipe**]({self.conf['thegoons']['bigP']})\n[Health]({self.conf['thegoons']['bigP']}#Notes)\n[Loot]({self.conf['thegoons']['bigP']}#Loot)\n[Strategy]({self.conf['thegoons']['bigP']}#Strategy)",
        )
        embed.add_field(
            inline=True,
            name="\u200b",
            value=f"[**Death Knight**]({self.conf['thegoons']['knight']})\n[Health]({self.conf['thegoons']['knight']}#Notes)\n[Loot]({self.conf['thegoons']['knight']}#Loot)\n[Strategy]({self.conf['thegoons']['knight']}#Strategy)",
        )
        embed.add_field(
            inline=True,
            name="\u200b",
            value=f"[**Birdeye**]({self.conf['thegoons']['birdeye']})\n[Health]({self.conf['thegoons']['birdeye']}#Notes)\n[Loot]({self.conf['thegoons']['birdeye']}#Loot)\n[Strategy]({self.conf['thegoons']['birdeye']}#Strategy)",
        )

        await interaction.followup.send(
            embed=embed, view=GoonsView(self.conf), ephemeral=True
        )


class GoonsView(discord.ui.View):
    def __init__(self, conf):
        super().__init__(timeout=None)

        for map in conf["thegoons"]["maps"]:
            self.add_item(
                GoonsSubButton(conf, label=f"{map.capitalize()} Map", custom_id=map)
            )

    async def on_timeout(self):
        self.clear_items()


class GoonsSubButton(discord.ui.Button):
    def __init__(self, conf, label, custom_id):
        self.conf = conf
        super().__init__(label=label, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        img = f"{self.conf['thegoons']['maps'][self.custom_id]}/revision/latest/scale-to-width-down/800"
        desc = f"[**Hi-res Here**]({self.conf['thegoons']['maps'][self.custom_id]})"
        embed: Embed = EB(
            title=f"The Goons - {self.custom_id.capitalize()}",
            description=desc,
            image_url=img,
        )

        await interaction.followup.send(embed=embed, ephemeral=True)
