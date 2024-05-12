from __future__ import annotations

import os, topgg, requests, json
from discord.ext import commands
from discord.ext import tasks

class tasks(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        super().__init__()
        self.bot = bot

        #### START TASKS ####
    
        dbl_token = os.getenv("TOPGG_TOKEN")
        self.topggpy = topgg.DBLClient(self.bot, dbl_token)
        self.update_stats.start()
        self.update_jsons.start()
        self.update_about.start()

    
    async def cog_unload(self) -> None:
        await self.topggpy.close()

    @tasks.loop(hours=3)
    async def update_jsons(self):
        if os.getenv("RUNTIME") == "DEV": return
        try:
            ammoJson = json.dumps((requests.get("https://api.tarkov-changes.com/v1/ammo", headers={"User-Agent": "Mozilla/5.0", "AUTH-TOKEN":os.getenv("AUTH_TOKEN")}, ).json())['results'])
            with open("./configs/data/ammunitions.json", "w") as f:
                f.write(ammoJson)
                f.close()
        except Exception as e:
            print(f"Failed to update ammo")

        try:
            armorJson = json.dumps((requests.get("https://api.tarkov-changes.com/v1/armor", headers={"User-Agent": "Mozilla/5.0", "AUTH-TOKEN":os.getenv("AUTH_TOKEN")}).json())['results'])
            with open("./configs/data/armors.json", "w") as f:
                f.write(armorJson)
                f.close()
        except Exception as e:
            print(f"Failed to update armor")

        try:
            bossJson = json.dumps((requests.get("https://api.tarkov-changes.com/v1/boss", headers={"User-Agent": "Mozilla/5.0", "AUTH-TOKEN":os.getenv("AUTH_TOKEN")}).json())['results'])
            with open("./configs/data/bosses.json", "w") as f:
                f.write(bossJson)
                f.close()
        except Exception as e:
            print(f"Failed to update bosses")

        try:
            bagJson = json.dumps((requests.get("https://api.tarkov-changes.com/v1/backpacks", headers={"User-Agent": "Mozilla/5.0", "AUTH-TOKEN":os.getenv("AUTH_TOKEN")}).json())['results'])
            with open("./configs/data/backpacks.json", "w") as f:
                f.write(bagJson)
                f.close()
        except Exception as e:
            print(f"Failed to update backpacks")

        try:
            helmJson = json.dumps((requests.get("https://api.tarkov-changes.com/v1/helmets", headers={"User-Agent": "Mozilla/5.0", "AUTH-TOKEN":os.getenv("AUTH_TOKEN")}).json())['results'])
            with open("./configs/data/helmets.json", "w") as f:
                f.write(helmJson)
                f.close()
        except Exception as e:
            print(f"Failed to update helmets")

        try:
            weaponJson = json.dumps((requests.get("https://api.tarkov-changes.com/v1/firearms", headers={"User-Agent": "Mozilla/5.0", "AUTH-TOKEN":os.getenv("AUTH_TOKEN")}).json())['results'])
            with open("./configs/data/firearms.json", "w") as f:
                f.write(weaponJson)
                f.close()
        except Exception as e:
            print(f"Failed to update firearms")

        try:
            bossJson = json.dumps((requests.get("https://api.tarkov-changes.com/v1/maps", headers={"User-Agent": "Mozilla/5.0", "AUTH-TOKEN":os.getenv("AUTH_TOKEN")}).json())['results'])
            with open("./configs/data/mapss.json", "w") as f:
                f.write(bossJson)
                f.close()
        except Exception as e:
            print(f"Failed to update bosses")

        print("JSONs Updated.")

    @update_jsons.before_loop
    async def before_update_about(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=30)
    async def update_stats(self):
        if os.getenv("RUNTIME") == "DEV": return
        """This function runs every 30 minutes to automatically update your server count."""
        try:
            await self.topggpy.post_guild_count()
            print(f"Posted server count ({self.topggpy.guild_count})")
        except Exception as e:
            print(f"Failed to post server count\n{e.__class__.__name__}: {e}")
        
        print("Stats Updated.")
    
    @update_stats.before_loop
    async def before_update_about(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=6)
    async def update_about(self):
        users = 0
        uniqueUsers = []
        for guild in self.bot.guilds:
            for user in guild.members:
                users += 1
                if user.id not in uniqueUsers: uniqueUsers.append(user.id)
        aboutJson = json.dumps({'users' : users, 'uniqueUsers' : len(uniqueUsers)})
        with open("./configs/data/about.json", "w") as f:
            f.write(aboutJson)
            f.close()

        print("About Updated.")
    
    @update_about.before_loop
    async def before_update_about(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(tasks(bot))