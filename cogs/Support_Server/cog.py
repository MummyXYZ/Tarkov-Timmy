from __future__ import annotations

import discord
import json
import os
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime, timedelta, timezone
from utils.embedbuilder import embedbuilder as EB
import logging
import logging.handlers
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("discord")


class Support_Server(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        if os.getenv("RUNTIME") == "DEV":
            return
        self.traders_Notified = {}
        self.traders_Restock_Notification.start()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if is_Guild_Tarkov_Timmy(member.guild):
            await send_Welcome_Message(member)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not is_Guild_Tarkov_Timmy(before.guild):
            return
        if "Server Booster" in after.roles:
            if "Server Booster" not in str(before.roles):
                announcements_chn = after.guild.get_channel(1252103463186333817)

                desc = f"{after.mention} boosted the server!"
                embed = EB(description=desc)

                announcements_chn.send(embed=embed)
        return

    @tasks.loop(seconds=5)
    async def traders_Restock_Notification(self):
        with open("./configs/data/traderresets.json", "r") as f:
            tradersJson = json.load(f)

        offset = 5
        time_Window = timedelta(minutes=offset)
        current_Time = datetime.now(timezone.utc)

        for trader in tradersJson:
            trader_Name = trader["name"]
            if trader_Name == "Lightkeeper" or trader_Name == "BTR Driver":
                continue

            traderTime = datetime.fromisoformat(trader["resetTime"])

            if (traderTime - time_Window) < current_Time < traderTime:
                if trader_Name not in self.traders_Notified:
                    self.traders_Notified[trader_Name] = False
                if self.traders_Notified[trader_Name]:
                    return

                trader_Announcement_Channel = self.bot.get_channel(1252613698816708708)
                trader_Announcement_Role = self.bot.get_guild(
                    1065456838658768956
                ).get_role(1252624330601267241)

                embed = EB(
                    description=f"🛒 {trader_Announcement_Role.mention} **{trader_Name}** restock within the next {offset} minutes!"
                )
                # Send message to channel
                announcement = await trader_Announcement_Channel.send(embed=embed)
                # Publish message to all guilds that follow
                await announcement.publish()

                self.traders_Notified[trader_Name] = True

            elif current_Time > traderTime:
                self.traders_Notified[trader_Name] = False
        return

    @traders_Restock_Notification.before_loop
    async def before_Traders_Restock_Notification(self):
        await self.bot.wait_until_ready()

    # @commands.Cog.listener()
    # async def on_message(self, message: discord.Message):
    #     if message.author.id != 170925319518158848:
    #         return
    #     desc = f"""{message.author.mention} boosted the server!"""

    #     embed = EB(description=desc)

    #     await message.channel.send(embed=embed)


async def send_Welcome_Message(member: discord.Member):
    welcome_Chnanel = member.guild.get_channel(int(os.getenv("WELCOME_CHANNEL_ID")))
    bot_Support_Forum = member.guild.get_channel(1241790880784973825)
    suggestions_Forum = member.guild.get_channel(1241790784764903564)

    desc = f"""Hey {member.mention}, Welcome to the **Tarkov Timmy** support server. Thanks for joining! Feel Free to look around.
    If you are having issues please start a post in {bot_Support_Forum.mention}.
    If you have a suggestion please start a post in {suggestions_Forum.mention}.
    
    **Shareable Invite Link:**
    > https://discord.gg/CC9v5aXNyY"""

    embed = EB(description=desc)

    await welcome_Chnanel.send(embed=embed)


def is_Guild_Tarkov_Timmy(guild: discord.Guild) -> bool:
    support_Guild = int(os.getenv("SUPPORT_SERVER_ID"))
    if guild.id == support_Guild:
        return True

    return False


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Support_Server(bot))
