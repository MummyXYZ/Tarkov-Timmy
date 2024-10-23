import discord
from discord import Embed
from utils.embedbuilder import embedbuilder as EB


class GoonsButton(discord.ui.Button):
    def __init__(self, conf, mapsJson):
        self.conf = conf
        self.mapsJson = mapsJson
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="The Goons",
            custom_id="goons",
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        description = "**Spawn chance:**\n"
        for map in self.mapsJson:
            for boss in map["bosses"]:
                if boss["boss"]["name"] == "Knight":
                    description += f"**{map['name'] if map['name'] != 'Ground Zero 21+' else 'Ground Zero'}**: {int(boss['spawnChance'] * 100)}%\n"

        description += "\nCheck out the </goons:1245395766374170644> command."

        embed = EB(
            title="The Goons",
            description=description,
            title_url=self.conf["thegoons"]["wiki"],
            image_url=self.conf["thegoons"]["img"],
        )

        links = [
            ("Big Pipe", self.conf["thegoons"]["bigP"]),
            ("Death Knight", self.conf["thegoons"]["knight"]),
            ("Birdeye", self.conf["thegoons"]["birdeye"]),
        ]
        for name, link in links:
            embed.add_field(
                inline=True,
                name=f"\u200b**{name}**",
                value=f"[Link]({link})\n[Health]({link}#Notes)\n[Loot]({link}#Loot)\n[Strategy]({link}#Strategy)",
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
