from mysql.connector import Error
from mysql.connector import pooling
import sys
import os
from dotenv import load_dotenv
load_dotenv()

try:
    cxnpool = pooling.MySQLConnectionPool(
        pool_size= 32,
        host= os.getenv("MySQL_HOST"),
        port= os.getenv("MySQL_PORT"),
        user= os.getenv("MySQL_USER"),
        password= os.getenv("MySQL_PASS"),
        database= os.getenv("MySQL_NAME"),
    )
    
except Error as e:
    print(f"Error connecting to MariaDB: {e}")
    sys.exit(1)

print("DB Connected")

async def query(query, params = None):
    try:
        cxn: pooling.MySQLConnection = cxnpool.get_connection()

        if cxn.is_connected():
            cur = cxn.cursor()
            cur.execute(query, params)

            result = cur.fetchall()
            return result
            
    except Error as e:
        print("Error while connecting to MySQL using Connection pool ", e)
    
    finally:
        if cxn.is_connected():
            cur.close()
            cxn.commit()
            cxn.close()

async def edit(query, params = None):
    try:
        cxn: pooling.MySQLConnection = cxnpool.get_connection()

        if cxn.is_connected():
            cur = cxn.cursor()
            cur.execute(query, params, multi=True)


            result = cur.rowcount
            return result
            
    except Error as e:
        print("Error while connecting to MySQL using Connection pool ", e)
    
    finally:
        if cxn.is_connected():
            cur.close()
            cxn.commit()
            cxn.close()