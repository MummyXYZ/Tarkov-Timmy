from __future__ import annotations

import discord
import traceback
import sys
import os
import topgg
import requests
import json
from discord.ext import commands
from discord.ext import tasks

import utils.guildhandler as GH

import logging
import logging.handlers

logger = logging.getLogger("discord")


#### Events
class Events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.bot.user.display_name} is ready!")

    @commands.Cog.listener()
    async def on_connect(self) -> None:
        logger.info("Connected to Discord gateway!")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await GH.create(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        await GH.delete(guild)


#### Error handling
class CommandErrorHandler(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """The event triggered when an error is raised while invoking a command.

        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, "on_error"):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound,)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, "original", error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f"{ctx.command} has been disabled.")

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(
                    f"{ctx.command} can not be used in Private Messages."
                )
            except discord.HTTPException:
                pass

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if (
                ctx.command.qualified_name == "tag list"
            ):  # Check if the command being invoked is 'tag list'
                await ctx.send("I could not find that member. Please try again.")

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            logger.error("Ignoring exception in command {}:".format(ctx.command))
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )


#### Recurring tasks
class Tasks(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        super().__init__()
        self.bot = bot

        dbl_token = os.getenv("TOPGG_TOKEN")
        self.topggpy = topgg.DBLClient(self.bot, dbl_token)
        self.update_stats.start()
        self.update_jsons.start()

    async def cog_unload(self) -> None:
        await self.topggpy.close()

    @tasks.loop(hours=3)
    async def update_jsons(self):
        if os.getenv("RUNTIME") == "DEV":
            return

        # Endpoint, File name
        data = [
            ["ammo", "ammunitions.json"],
            ["boss", "bosses.json"],
            ["maps", "maps.json"],
        ]

        for item in data:
            try:
                data = json.dumps(
                    (
                        requests.get(
                            "https://api.tarkov-changes.com/v1/" + item[0],
                            headers={
                                "User-Agent": "Mozilla/5.0",
                                "AUTH-TOKEN": os.getenv("AUTH_TOKEN"),
                            },
                        ).json()
                    )["results"]
                )
                with open("./configs/data/" + item[1], "w") as f:
                    f.write(data)
                    f.close()
            except Exception:
                logger.error("Failed to update " + item[0])

        logger.info("JSONs Updated.")

    @update_jsons.before_loop
    async def before_update_jsons(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=30)
    async def update_stats(self):
        if os.getenv("RUNTIME") == "DEV":
            return
        """This function runs every 30 minutes to automatically update your server count."""
        try:
            await self.topggpy.post_guild_count()
            logger.info(f"Posted server count ({self.topggpy.guild_count})")
        except Exception as e:
            logger.error(f"Failed to post server count\n{e.__class__.__name__}: {e}")

        logger.info("Stats Updated.")

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Events(bot))
    await bot.add_cog(CommandErrorHandler(bot))
    await bot.add_cog(Tasks(bot))
