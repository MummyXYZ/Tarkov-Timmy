from __future__ import annotations

import os
import sys
import psycopg2
import psycopg2.pool
import psycopg2.extras
import logging
import logging.handlers
import traceback
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


# def execute(query, params=None):
#     # try:
#     cxn: psycopg2.extensions.connection = pool.getconn()

#     if not cxn.closed:
#         cur = cxn.cursor()
#         cur.execute(query, params)

#         print(cur.rowcount)

#         # result = cur.fetchall()
#         # return result

#     # except Exception as e:
#     #     logger.error(f"Error while connecting to postgresql using Connection pool: {e}")
#     #     # traceback.print_stack()

#     # finally:
#     #     if not cxn.closed:
#     #         cur.close()
#     #         cxn.commit()694707513764872202
#     #         cxn.close()


def execute(query, params=None):
    cxn: psycopg2.extensions.connection = pool.getconn()

    if not cxn.closed:
        cur = cxn.cursor()
        cur.execute(query, params)

        result = cur.fetchall()
        cur.close()
        cxn.commit()
        cxn.close()
        return result


def update(query, params=None):
    cxn: psycopg2.extensions.connection = pool.getconn()

    if not cxn.closed:
        cur = cxn.cursor()
        cur.execute(query, params)

        result = cur.rowcount
        cur.close()
        cxn.commit()
        cxn.close()
        return result


def insert(query, params=None):
    cxn: psycopg2.extensions.connection = pool.getconn()

    if not cxn.closed:
        cur = cxn.cursor()
        cur.execute(query, params)

        cur.close()
        cxn.commit()
        cxn.close()


def delete(query, params=None):
    cxn: psycopg2.extensions.connection = pool.getconn()

    if not cxn.closed:
        cur = cxn.cursor()
        cur.execute(query, params)

        cur.close()
        cxn.commit()
        cxn.close()
