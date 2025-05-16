from fastapi import Depends
from app.db.session import get_db_connection
from aiomysql import Connection

async def get_db() -> Connection:
    """
    Database connection dependency.
    Yields a database connection and ensures it's closed after use.
    """
    conn = await get_db_connection()
    try:
        yield conn
    finally:
        conn.close() 