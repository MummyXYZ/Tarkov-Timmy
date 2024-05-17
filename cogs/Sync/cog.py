from __future__ import annotations

from discord.ext import commands


class Sync(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        await ctx.defer(ephemeral=True)
        synced_commands = await self.bot.tree.sync()
        await ctx.reply(
            f"Successfully synced {len(synced_commands)} commands.", ephemeral=True
        )


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Sync(bot))
