import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

dbconfig = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "shopscaledb"),
}

class DatabasePool:
    def __init__(self):
        self.pool = pooling.MySQLConnectionPool(
            pool_name="shopscale_pool",
            pool_size=10,
            **dbconfig
        )

    def get_connection(self):
        return self.pool.get_connection()

# Create a global pool instance
db_pool = DatabasePool()