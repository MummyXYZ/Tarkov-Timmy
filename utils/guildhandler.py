from discord import Guild
import utils.db as db

async def create(guild: Guild):
    query = """INSERT INTO perms (guild_id, target_id, add_perm, edit, remove, leaderboard, list, perms) VALUES (%s, %s, 1, 1, 0, 1, 1, 0)"""
    params = (guild.id, guild.id)
    await db.query(query, params)

    query = f"""INSERT INTO guild (guild_id) VALUES ({guild.id})"""
    await db.query(query)

    print(f"{guild.name} added.")

async def delete(guild: Guild):
    query = f"""DELETE FROM perms WHERE guild_id = {guild.id}"""
    await db.query(query)

    query = f"""DELETE FROM tk_entries WHERE guild_id = {guild.id}"""
    await db.query(query)

    query = f"""DELETE FROM guild WHERE guild_id = {guild.id}"""
    await db.query(query)

    print(guild.id)
    print(f"{guild.name} removed.")