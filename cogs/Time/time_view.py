import discord
from datetime import datetime, timedelta, timezone

VIEW_NAME = "TimeView"


class TimeView(discord.ui.View):
    def __init__(self):
        def inGameTime(left) -> str:
            utc_Time = datetime.now(timezone.utc).timestamp()
            leftOffset = timedelta(hours=0) if left else timedelta(hours=12)
            russiaOffset = timedelta(hours=7)
            tarkyMultiplier = 7
            tarkyTime = (
                datetime.fromtimestamp(((utc_Time * tarkyMultiplier) % 86400000))
                + russiaOffset
                + leftOffset
            )
            tarkyTimeF = tarkyTime.strftime("%H:%M:%S")
            return tarkyTimeF

        super().__init__(timeout=None)
        self.add_item(
            TimeButton(
                custom_id=f"{VIEW_NAME}:time_button",
                label=f"{inGameTime(True)} ⌚ {inGameTime(False)}",
            )
        )

    async def on_timeout(self):
        self.clear_items()


class TimeButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=TimeView())
