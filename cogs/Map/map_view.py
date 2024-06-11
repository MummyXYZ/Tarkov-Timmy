import discord
from discord import Embed
from discord.ui import Button
from .goons import GoonsButton
from .cult import CultButton
from utils.embedbuilder import embedbuilder as EB

VIEW_NAME = "MapView"


class MapView(discord.ui.View):
    def __init__(self, map, conf, mapsJson):
        super().__init__(timeout=None)

        # Get the interactive button URL for the current map
        interactive_button = conf["locations"][map].get("interactive")
        if interactive_button:
            # Add an interactive button to the view if the URL exists
            self.add_item(Button(label="Interactive", url=interactive_button))

        # Iterate over the map links in the configuration
        for mapLink in conf["locations"][map]:
            # Exclude certain map links
            if mapLink not in {
                "base",
                "interactive",
            }:
                # Add a map button for each map link
                self.add_item(MapButton(map, mapLink, conf))

        if map == "Ground Zero":
            map = "Ground Zero 21+"
        for mapData in mapsJson:
            if mapData["name"] == map:
                for boss in mapData["bosses"]:
                    if boss["boss"]["name"] == "Death Knight":
                        self.add_item(GoonsButton(conf, mapsJson))

                    if boss["boss"]["name"] == "Cultist Priest":
                        self.add_item(CultButton(conf, mapsJson))

    async def on_timeout(self):
        self.clear_items()


class MapButton(discord.ui.Button):
    def __init__(self, map, mapLink, conf):
        self.map = map
        self.conf = conf
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="2D" if mapLink == "map" else mapLink,
            custom_id=mapLink,
        )

    async def callback(self, interaction: discord.Interaction):
        # Set the author of the embed based on the map link
        author = "2D Map" if self.custom_id == "map" else f"{self.custom_id} Map"

        # Get the image URL for the map
        img = f"{self.conf['locations'][self.map][self.custom_id]}/revision/latest/scale-to-width-down/1000"

        # Defer the response and create the embed
        await interaction.response.defer(ephemeral=True)
        embed: Embed = EB(
            author=author,
            description=f"[**Hi-res Here**]({self.conf['locations'][self.map][self.custom_id]})",
            image_url=img,
        )

        # Send the embed in a follow-up message
        await interaction.followup.send(embed=embed, ephemeral=True)
