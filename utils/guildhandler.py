from discord import Guild
import utils.db as db
import json

import logging

logger = logging.getLogger("discord")


async def create(guild: Guild):
    default_perms = json.dumps(
        {
            guild.id: {
                "add": True,
                "edit": True,
                "remove": False,
                "leaderboard": True,
                "list": True,
                "perms": False,
            }
        }
    )

    query = "INSERT INTO tk_bot.guilds (guild_id, guild_name) VALUES (%s, %s) ON CONFLICT DO NOTHING"
    params = (
        guild.id,
        guild.name,
    )
    db.insert(query, params)

    query = "INSERT INTO tk_bot.perms (guild_id, guild_name, perms) VALUES (%s, %s, %s) ON CONFLICT (guild_id) DO UPDATE SET perms = %s"
    params = (
        guild.id,
        guild.name,
        default_perms,
        default_perms,
    )
    db.insert(query, params)

    logger.info(f"{guild.name} added.")


async def delete(guild: Guild):
    query = "DELETE FROM tk_bot.perms WHERE guild_id = '%s'"
    params = (guild.id,)
    db.delete(query, params)

    query = "DELETE FROM tk_bot.entries WHERE guild_id = '%s'"
    params = (guild.id,)
    db.delete(query, params)

    query = "DELETE FROM tk_bot.guilds WHERE guild_id = %s"
    params = (guild.id,)
    db.delete(query, params)

    logger.info(f"{guild.name} removed.")
