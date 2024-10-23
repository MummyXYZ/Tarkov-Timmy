from discord import Guild
import utils.db as db
import json
import logging
import traceback

logger = logging.getLogger("discord")


async def create(guild: Guild):
    try:
        # Default permissions as a JSON string
        default_perms = json.dumps({guild.id: {
            "add": True, "edit": True, "remove": False, "leaderboard": True, "list": True, "perms": False
        }})

        # Get the Guild Icon URL
        guild_icon_url = guild.icon.url if guild.icon else None

        # Get the Guild Member Count
        guild_member_count = guild.member_count

        async with db.pool.acquire() as cxn:
            async with cxn.transaction():
                # Insert or update guild_name, guild_icon, and member_count in the 'guilds' table
                query = """
                    INSERT INTO tk_bot.guilds (guild_id, guild_name, guild_icon, member_count)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (guild_id) DO UPDATE 
                    SET guild_name = EXCLUDED.guild_name, 
                        guild_icon = EXCLUDED.guild_icon, 
                        member_count = EXCLUDED.member_count
                """
                params = (guild.id, guild.name,
                          guild_icon_url, guild_member_count)
                await cxn.execute(query, *params)

                # Insert or update permissions in the 'perms' table
                query = """
                    INSERT INTO tk_bot.perms (guild_id, guild_name, perms)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (guild_id) DO UPDATE 
                    SET guild_name = EXCLUDED.guild_name
                """
                params = (guild.id, guild.name, default_perms)
                await cxn.execute(query, *params)

                logger.info(f"{guild.name} added/updated.")
    except Exception as e:
        logger.error(f"Error creating/updating guild {guild.name}: {e}")
        traceback.print_exc()


async def delete(guild: Guild):
    try:
        async with db.pool.acquire() as cxn:
            async with cxn.transaction():
                query = "DELETE FROM tk_bot.perms WHERE guild_id = $1"
                await cxn.execute(query, guild.id)

                query = "DELETE FROM tk_bot.entries WHERE guild_id = $1"
                await cxn.execute(query, guild.id)

                query = "DELETE FROM tk_bot.guilds WHERE guild_id = $1"
                await cxn.execute(query, guild.id)

        logger.info(f"{guild.name} removed.")
    except Exception as e:
        logger.error(f"Error deleting guild {guild.name}: {e}")
        traceback.print_exc()
