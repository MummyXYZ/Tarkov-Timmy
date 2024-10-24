from __future__ import annotations

import discord
import traceback
import sys
import os
import topgg
import aiohttp
import json
from discord.ext import commands
from discord.ext import tasks
from itertools import cycle
import utils.guildhandler as GH
import logging
import logging.handlers


logger = logging.getLogger("discord")


# Events
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


# Error handling
class CommandErrorHandler(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
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
            logger.error(
                "Ignoring exception in command {}:".format(ctx.command))
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )


# Recurring tasks
class Tasks(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        super().__init__()
        self.bot = bot
        self.statuses = cycle(
            [
                "Check out /help",
                "Extract Camping",
                "Beat the Chads!",
                "You can't escape Tarkov",
                "Is it wipe yet?",
                "☠️(Head, Eyes)",
                "Maybe Chad? Maybe Luck?",
                "Timmys for life",
            ]
        )

        dbl_token = os.getenv("TOPGG_TOKEN")
        self.topggpy = topgg.DBLClient(self.bot, dbl_token)
        self.update_stats.start()
        self.update_data.start()
        self.update_goons.start()
        self.update_traders.start()
        self.update_status.start()
        # self.update_weather.start()

    async def cog_unload(self) -> None:
        self.update_stats.cancel()
        self.update_data.cancel()
        self.update_goons.cancel()
        self.update_traders.cancel()
        self.update_status.cancel()
        # self.update_weather.cancel()

        await self.topggpy.close()

    @tasks.loop(seconds=30)
    async def update_status(self):
        await self.bot.change_presence(
            activity=discord.CustomActivity(name=next(self.statuses))
        )
        return

    @update_status.before_loop
    async def before_update_status(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1)
    async def update_goons(self):
        endpoints = [("https://tarkovpal.com/api", "goons.json")]

        for endpoint, filename in endpoints:
            headers = {"User-Agent": "Mozilla/5.0"}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint, headers=headers) as r:
                        if r.status == 200:
                            data = await r.text()

                            with open(f"./configs/data/{filename}", "w") as f:
                                f.write(data)

            except aiohttp.ClientError:
                logger.error(f"Failed to update {endpoint}")

        logger.debug("Goons Updated.")
        return

    @update_goons.before_loop
    async def before_update_goons(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=3)
    async def update_data(self):
        dataPoints = [
            ("ammo", "ammunitions.json"),
            ("maps", "maps.json"),
        ]

        query = """
        {
            ammo {
                item {
                name
                shortName
                }
                caliber
                penetrationPower
                damage
                fragmentationChance
                recoilModifier
                projectileCount
            }
            maps {
                name
                wiki
                players
                description
                raidDuration
                
                bosses {
                boss {
                    name
                }
                escorts {
                    amount {
                        count
                    }
                }
                spawnChance
                }
            }
        }"""

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.tarkov.dev/graphql",
                    headers=headers,
                    json={"query": query},
                ) as r:
                    if r.status == 200:
                        data = json.loads(await r.text())["data"]
                        for selector, filename in dataPoints:
                            if data[selector] is not None:
                                with open(f"./configs/data/{filename}", "w") as f:
                                    f.write(json.dumps(data[selector]))
                    else:
                        raise Exception(
                            "Query failed to run by returning code of {}. {}".format(
                                r.status, query
                            )
                        )

                    logger.debug("Data Updated.")

        except (json.JSONDecodeError, aiohttp.ClientError):
            logger.error("Failed to update Data")

        return

    @update_data.before_loop
    async def before_update_data(self):
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
        return

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=5)
    async def update_traders(self):
        dataPoints = [
            ("traders", "traderresets.json"),
        ]

        query = """
        {
            traders {
                name
                resetTime
            }
        }"""

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.tarkov.dev/graphql",
                    headers=headers,
                    json={"query": query},
                ) as r:
                    if r.status == 200:
                        data = json.loads(await r.text())["data"]

                        for selector, filename in dataPoints:
                            with open(f"./configs/data/{filename}", "w") as f:
                                f.write(json.dumps(data[selector]))

                        logger.debug("Traders Updated.")
                    else:
                        raise Exception(
                            "Query failed to run by returning code of {}. {}".format(
                                r.status, query
                            )
                        )

        except (json.JSONDecodeError, aiohttp.ClientError):
            logger.error("Failed to update Traders")
        return

    @update_traders.before_loop
    async def before_update_traders(self):
        await self.bot.wait_until_ready()

    # @tasks.loop(minutes=5)
    # async def update_weather(self):
    #     """Fetch and update the weather information every 5 minutes."""
    #     endpoints = [
    #         "https://api.tarkov-changes.com/v1/weather",
    #         "weather.json",
    #     ]
    #     headers = {
    #         "User-Agent": "Mozilla/5.0",
    #         "AUTH-TOKEN": os.getenv("AUTH_TOKEN"),
    #     }

    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             async with session.get(endpoints[0], headers=headers) as response:
    #                 if response.status != 200:
    #                     logger.error(f"Failed to fetch weather data: {
    #                                  response.status}")
    #                     return

    #                 data = await response.json()
    #                 weather_results = data.get("results")

    #                 # Process the weather results
    #                 if not weather_results:
    #                     logger.error(
    #                         "No weather data found in the API response")
    #                     return

    #                 # Alert if rain intensity is not zero
    #                 if weather_results[0].get("rain_intensity", 0.0) != 0.0:
    #                     channel = await self.bot.fetch_channel("1029456229510172754")
    #                     await channel.send(f"<@170925319518158848> {json.dumps(weather_results)}")

    #                 # Write weather data to the file
    #                 with open(f"./configs/data/{endpoints[1]}", "w") as f:
    #                     json.dump(weather_results, f)

    #                 logger.debug(f"Weather data updated and written to {
    #                              endpoints[1]}")

    #     except aiohttp.ClientError as e:
    #         logger.error(f"Failed to update {endpoints[0]}: {str(e)}")
    #     except json.JSONDecodeError as e:
    #         logger.error(f"Failed to decode JSON from {
    #                      endpoints[0]}: {str(e)}")

    # @update_weather.before_loop
    # async def before_update_weather(self):
    #     """Wait until the bot is ready before starting the weather updates."""
    #     await self.bot.wait_until_ready()


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Events(bot))
    await bot.add_cog(CommandErrorHandler(bot))
    await bot.add_cog(Tasks(bot))
