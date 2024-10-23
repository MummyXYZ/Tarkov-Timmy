from __future__ import annotations

from discord.ext import commands

import logging
import logging.handlers

logger = logging.getLogger("discord")


class Sync(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        await ctx.defer(ephemeral=True)

        try:
            synced_commands = await self.bot.tree.sync()
            logger.info(f"Successfully synced {len(synced_commands)} commands. Command details: {synced_commands}")

            await ctx.reply(
                f"Successfully synced {len(synced_commands)} commands.", ephemeral=True
            )
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
            await ctx.reply(f"Error syncing commands: {str(e)}", ephemeral=True)

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(Sync(bot))
