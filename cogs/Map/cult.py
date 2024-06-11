import discord
from discord import Embed
from utils.embedbuilder import embedbuilder as EB


class CultButton(discord.ui.Button):
    def __init__(self, conf, mapsJson):
        self.conf = conf
        self.mapsJson = mapsJson
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="Cultists",
            custom_id="cult",
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        description = "**Spawn chance:**\n"
        for map in self.mapsJson:
            for boss in map["bosses"]:
                if boss["boss"]["name"] == "Cultist Priest":
                    description += f"**{map['name'] if map['name'] != 'Ground Zero 21+' else 'Ground Zero'}**: {int(boss['spawnChance'] * 100)}%\n"

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
