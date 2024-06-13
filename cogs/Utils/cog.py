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
        self.update_data.start()
        self.update_goons.start()

    async def cog_unload(self) -> None:
        await self.topggpy.close()

    @tasks.loop(minutes=1)
    async def update_goons(self):
        endpoints = [("https://tarkovpal.com/api", "goons.json")]

        for endpoint, filename in endpoints:
            headers = {"User-Agent": "Mozilla/5.0"}
            try:
                response = requests.get(endpoint, headers=headers)
                response.raise_for_status()
                data = json.dumps(response.json())

                with open(f"./configs/data/{filename}", "w") as f:
                    f.write(data)

            except (requests.RequestException, json.JSONDecodeError):
                logger.error(f"Failed to update {endpoint}")

        logger.debug("Goons Updated.")
        return

    @update_goons.before_loop
    async def before_update_goons(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=5)
    async def update_data(self):
        dataPoints = [
            ("ammo", "ammunitions.json"),
            ("maps", "maps.json"),
            ("traderResetTimes", "traderresets.json"),
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
            traderResetTimes {
                name
                resetTimestamp
            }
        }"""

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
        }
        response = requests.post(
            "https://api.tarkov.dev/graphql", headers=headers, json={"query": query}
        )

        if response.status_code == 200:
            for selector, filename in dataPoints:
                with open(f"./configs/data/{filename}", "w") as f:
                    f.write(json.dumps(response.json()["data"][selector]))
        else:
            raise Exception(
                "Query failed to run by returning code of {}. {}".format(
                    response.status_code, query
                )
            )

        logger.debug("Data Updated.")
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


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Events(bot))
    await bot.add_cog(CommandErrorHandler(bot))
    await bot.add_cog(Tasks(bot))

    # @tasks.loop(minutes=5)
    # async def update_weather(self):
    #     endpoints = [
    #         "https://api.tarkov-changes.com/v1/weather",
    #         "weather.json",
    #     ]
    #     headers = {
    #         "User-Agent": "Mozilla/5.0",
    #         "AUTH-TOKEN": os.getenv("AUTH_TOKEN"),
    #     }
    #     try:
    #         response = requests.get(endpoints[0], headers=headers)
    #         response.raise_for_status()
    #         data = json.dumps(response.json()["results"])
    #         print(endpoints[1])
    #         if response.json()["results"][0]["rain_intensity"] != 0.0:
    #             channel = await self.bot.fetch_channel("1029456229510172754")
    #             await channel.send(f"<@170925319518158848> {data}")
    #         print(data)

    #         with open(f"./configs/data/{endpoints[1]}", "w") as f:
    #             f.write(data)

    #     except (requests.RequestException, json.JSONDecodeError):
    #         logger.error(f"Failed to update {endpoints[0]}")

    #     logger.debug("Weather Updated.")
    #     return

    # @update_weather.before_loop
    # async def before_update_weather(self):
    #     await self.bot.wait_until_ready()

    # if (
    #     data["cloud"] >= -0.7
    #     and data["wind_speed"] <= 1
    #     and data["rain"] > 1
    #     and data["rain"] <= 3
    # ):
    #     weather_info["icon"] = "fa-cloud-sun-rain"
    #     weather_info["raining"] = "Yes"
    # elif data["wind_speed"] <= 1 and data["rain"] > 3:
    #     weather_info["icon"] = "fa-cloud-rain"
    #     weather_info["raining"] = "Yes"
    # elif (
    #     data["cloud"] < -0.4
    #     and data["wind_speed"] <= 1
    #     and data["rain"] < 2
    #     and data["fog"] <= 0.004
    #     or data["cloud"] < -0.4
    #     and data["wind_speed"] > 1
    #     and data["rain"] < 2
    #     and data["fog"] <= 0.004
    # ):
    #     weather_info["icon"] = "fa-sun"
    # elif (
    #     data["cloud"] >= -0.7
    #     and data["cloud"] <= -0.4
    #     and data["wind_speed"] <= 1
    #     and data["rain"] < 2
    #     and data["fog"] <= 0.004
    # ):
    #     weather_info["icon"] = "fa-clouds-sun"
    # elif data["cloud"] < -0.4 and data["fog"] > 0.004 and data["fog"] < 0.1:
    #     weather_info["icon"] = "fa-sun-haze"
    #     weather_info["foggy"] = "Yes"
    # elif data["fog"] >= 0.1:
    #     weather_info["icon"] = "fa-cloud-fog"
    # elif data["cloud"] >= -0.4 and data["cloud"] <= 0.7 and data["fog"] > 0.004:
    #     weather_info["icon"] = "fa-cloud-fog"
    #     weather_info["foggy"] = "Yes"
    # elif data["cloud"] >= -0.4 and data["cloud"] <= 0.7 and data["rain"] <= 1:
    #     weather_info["icon"] = "fa-clouds-sun"
    # elif data["cloud"] >= 0.7 and data["cloud"] <= 1 and data["rain"] <= 1:
    #     weather_info["icon"] = "fa-clouds"
    # elif data["cloud"] >= 1 and data["rain"] <= 1:
    #     weather_info["icon"] = "fa-cloud-bolt"
    #     weather_info["raining"] = "Yes"
    # elif data["cloud"] >= 0 and data["wind_speed"] >= 2 and data["rain"] <= 1:
    #     weather_info["icon"] = "fa-clouds"
    # elif data["wind_speed"] >= 2 and data["rain"] >= 2:
    #     weather_info["icon"] = "fa-cloud-rain"
    #     weather_info["raining"] = "Yes"
    # else:
    #     weather_info["icon"] = "fa-exclamation"
    #     weather_info["raining"] = "NO WEATHER FOUND"

    # weather_info_html = """
    # <i class="fa-solid {icon} sisterSiteSVG sisterSiteFA"></i>
    # <p>Temperature: {temperature} &#176;C</p>
    # <p>Pressure: {pressure} Hg</p>
    # <p>Wind Speed: {wind_speed} km/h</p>
    # <p>Raining: {raining}</p>
    # <p>Foggy: {foggy}</p>
    # <p>{metar}</p>
    # """.format(**weather_info)
