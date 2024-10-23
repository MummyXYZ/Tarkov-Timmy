import discord
from discord import Embed
from discord.ui import Button
from .goons import GoonsButton
from .cult import CultButton
from utils.embedbuilder import embedbuilder as EB


class MapView(discord.ui.View):
    def __init__(self, map_name, conf, maps_json):
        super().__init__(timeout=None)

        # Add an interactive button if the URL exists
        interactive_button = conf["locations"][map_name].get("interactive")
        if interactive_button:
            self.add_item(Button(label="Interactive", url=interactive_button))

        # Add map buttons excluding base and interactive
        map_links = {
            link: label
            for link, label in conf["locations"][map_name].items()
            if link not in {"base", "interactive"}
        }
        for map_link in map_links:
            self.add_item(MapButton(map_name, map_link, conf))

        # Adjust map name for "Ground Zero"
        map_name = "Ground Zero 21+" if map_name == "Ground Zero" else map_name

        # Add buttons based on bosses in the map
        for map_data in maps_json:
            if map_data["name"] == map_name:
                for boss in map_data.get("bosses", []):
                    boss_name = boss["boss"]["name"]
                    if boss_name == "Knight":
                        self.add_item(GoonsButton(conf, maps_json))
                    elif boss_name == "Cultist Priest":
                        self.add_item(CultButton(conf, maps_json))

    async def on_timeout(self):
        self.clear_items()


class MapButton(discord.ui.Button):
    def __init__(self, map_name, map_link, conf):
        label = "2D" if map_link == "map" else map_link
        super().__init__(style=discord.ButtonStyle.primary, label=label, custom_id=map_link)
        self.map_name = map_name
        self.conf = conf

    async def callback(self, interaction: discord.Interaction):
        # Set the author of the embed and the image URL based on the map link
        author = "2D Map" if self.custom_id == "map" else f"{self.custom_id} Map"
        image_url = f"{self.conf['locations'][self.map_name][self.custom_id]}/revision/latest/scale-to-width-down/1000"

        # Defer response and send the map image embed
        await interaction.response.defer(ephemeral=True)
        embed: Embed = EB(
            author=author,
            description=f"[**Hi-res Here**]({self.conf['locations'][self.map_name][self.custom_id]})",
            image_url=image_url,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
