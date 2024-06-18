import discord
from discord.ext import commands
import os
from utils.embedbuilder import embedbuilder as EB
import logging
import logging.handlers
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("discord")


class Temp(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if is_Guild_Tarkov_Timmy(member.guild):
            await send_Welcome_Message(member)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if "Server Booster" in after.roles:
            if "Server Booster" not in str(before.roles):
                announcements_chn = after.guild.get_channel(1252103463186333817)

                desc = f"{after.mention} boosted the server!"
                embed = EB(description=desc)

                announcements_chn.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        desc = f"""Hey {message.author.mention}, Welcome to the **Tarkov Timmy** support server. Thanks for joining! Feel Free to look around.

        If you are having issues please start a post in .
        If you have a suggestion please start a post in .
        
        **Shareable Invite Link:**
        > https://discord.gg/CC9v5aXNyY
        
        User boosted the server!"""

        embed = EB(description=desc)

        await message.channel.send(embed=embed)


def is_Guild_Tarkov_Timmy(guild: discord.Guild) -> bool:
    support_Guild = int(os.getenv("SUPPORT_SERVER_ID"))
    if guild.id == support_Guild:
        return True

    return False


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


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Temp(bot))
