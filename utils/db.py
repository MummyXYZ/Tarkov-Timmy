from __future__ import annotations

import os
import sys
import psycopg2
import psycopg2.pool
import psycopg2.extras
import logging
import logging.handlers
from dotenv import load_dotenv

logger = logging.getLogger("discord")
load_dotenv()

pg_connection_dict = {
    "minconn": 2,
    "maxconn": 32,
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

try:
    pool = psycopg2.pool.SimpleConnectionPool(**pg_connection_dict)
except Exception as e:
    logger.error(f"Error connecting to postgresql: {e}")
    sys.exit(1)


def execute(query: str, params=None) -> list:
    """
    Executes a query and returns the result
    """
    cxn = pool.getconn()
    try:
        cur = cxn.cursor()
        cur.execute(query, params)
        result = cur.fetchall()
        cur.close()
        cxn.commit()
        cxn.close()
        return result
    except Exception as e:
        cxn.rollback()
        cur.close()
        cxn.close()
        raise e


def update(query: str, params=None) -> int:
    """
    Executes an update query and returns the number of affected rows
    """
    cxn = pool.getconn()
    try:
        cur = cxn.cursor()
        cur.execute(query, params)
        result = cur.rowcount
        cur.close()
        cxn.commit()
        cxn.close()
        return result
    except Exception as e:
        cxn.rollback()
        cur.close()
        cxn.close()
        raise e


def insert(query: str, params=None) -> None:
    """
    Executes an insert query
    """
    cxn = pool.getconn()
    try:
        cur = cxn.cursor()
        cur.execute(query, params)
        cur.close()
        cxn.commit()
        cxn.close()
    except Exception as e:
        cxn.rollback()
        cur.close()
        cxn.close()
        raise e


def delete(query: str, params=None) -> None:
    """
    Executes a delete query
    """
    cxn = pool.getconn()
    try:
        cur = cxn.cursor()
        cur.execute(query, params)
        cur.close()
        cxn.commit()
        cxn.close()
    except Exception as e:
        cxn.rollback()
        cur.close()
        cxn.close()
        raise e
