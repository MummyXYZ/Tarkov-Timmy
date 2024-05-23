from __future__ import annotations

import os
import sys
import asyncio
import asyncpg
import logging
import logging.handlers
from dotenv import load_dotenv

logger = logging.getLogger("discord")
load_dotenv()

pg_connection_dict = {
    "min_size": 2,
    "max_size": 32,
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

pool = None


async def create_pool():
    global pool
    try:
        pool = await asyncpg.create_pool(**pg_connection_dict)
    except Exception as e:
        logger.error(f"Error connecting to postgresql: {e}")
        sys.exit(1)


async def fetch(query: str, *params) -> list:
    """
    Executes a query and returns the result
    """
    async with pool.acquire() as cxn:
        result = await cxn.fetch(query, *params)
        return result


async def execute(query: str, *params) -> int:
    """
    Executes an update query and returns the number of affected rows
    """
    async with pool.acquire() as cxn:
        result = await cxn.execute(query, *params)
        return result.strip("UPDATE ")


async def insert(query: str, *params) -> None:
    """
    Executes an insert query
    """
    async with pool.acquire() as cxn:
        await cxn.execute(query, *params)


async def delete(query: str, *params) -> None:
    """
    Executes a delete query
    """
    async with pool.acquire() as cxn:
        await cxn.execute(query, *params)


asyncio.create_task(create_pool())
