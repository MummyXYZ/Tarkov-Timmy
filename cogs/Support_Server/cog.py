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
    async def on_ready(self):
        try:
            self.support_Server = self.bot.get_guild(int(os.getenv("SUPPORT_SERVER_ID")))
            if self.support_Server is None:
                logger.error("Support server not found!")
                return
            
            self.announcements_Channel = self.support_Server.get_channel(int(os.getenv("ANNOUNCEMENTS_CHANNEL_ID")))
            self.bot_Support_Forum = self.support_Server.get_channel(1241790880784973825)
            self.trader_Announcement_Channel = self.support_Server.get_channel(
                int(os.getenv("TRADER_ANNOUNCEMENTS_CHANNEL_ID"))
            )
            self.trader_Announcement_Role = self.support_Server.get_role(
                int(os.getenv("TRADER_ANNOUNCEMENT_ROLE_ID"))
            )
            
            logger.info("Successfully set up support server channels and roles.")
        except Exception as e:
            logger.error(f"Error in on_ready: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if self.is_Guild_Tarkov_Timmy(member.guild):
            try:
                await send_Welcome_Message(member)
            except Exception as e:
                logger.error(f"Failed to send welcome message to {member.name}: {e}")


    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not self.is_Guild_Tarkov_Timmy(before.guild):
            return
        
        server_booster_role_id = 1000000000000000000  # Discord's static Server Booster role ID
        server_booster_role = discord.utils.get(after.guild.roles, id=server_booster_role_id)
        
        if not server_booster_role:
            return
        
        # Check if the user gained the Server Booster role
        if server_booster_role in after.roles and server_booster_role not in before.roles:
            desc = f"{after.mention} boosted the server!"
            embed = EB(description=desc)
            await self.announcements_Channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        if self.is_Guild_Tarkov_Timmy(thread.guild):
            if thread.parent_id == self.bot_Support_Forum.id:
                reply = f"Hello {thread.owner.mention}, please do not unfollow this forum, do not ping anyone and do not make duplicates. If no one responds to your thread within 12hrs, ping <@&1065469238149652490> Thanks!"
                await thread.send(reply)

    @tasks.loop(seconds=5)
    async def traders_Restock_Notification(self):
        if not os.path.exists("./configs/data/traderresets.json"):
            logger.error("traderresets.json not found!")
            return
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

                embed = EB(
                    description=f"🛒 **{trader_Name}** restock within the next {offset} minutes!"
                )
                # Send message to channel
                announcement = await self.trader_Announcement_Channel.send(
                    content=self.trader_Announcement_Role.mention, embed=embed
                )
                # Publish message to all guilds that follow
                await announcement.publish()

                self.traders_Notified[trader_Name] = True

            elif current_Time > traderTime:
                self.traders_Notified[trader_Name] = False

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

    def is_Guild_Tarkov_Timmy(self, guild: discord.Guild) -> bool:
        # Ensure that self.support_Server is set
        if not hasattr(self, 'support_Server') or self.support_Server is None:
            logger.error("Support server is not initialized.")
            return False
        
        return guild.id == self.support_Server.id




async def send_Welcome_Message(member: discord.Member):
    welcome_Chnanel = member.guild.get_channel(int(os.getenv("WELCOME_CHANNEL_ID")))
    bot_Support_Forum = member.guild.get_channel(1241790880784973825)
    suggestions_Forum = member.guild.get_channel(1241790784764903564)

    desc = f"""Welcome to the **Tarkov Timmy** support server. Thanks for joining! Feel Free to look around.
    If you are having issues please start a post in {bot_Support_Forum.mention}.
    If you have a suggestion please start a post in {suggestions_Forum.mention}.
    
    **Shareable Invite Link:**
    > https://discord.gg/CC9v5aXNyY"""

    embed = EB(description=desc)

    await welcome_Chnanel.send(content=f"Hey {member.mention}!", embed=embed)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Support_Server(bot))
