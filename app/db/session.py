from aiomysql import create_pool
from app.core.config import settings

async def get_db_pool():
    return await create_pool(
        host=settings.MYSQL_HOST,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        db=settings.MYSQL_DATABASE,
        minsize=1,
        maxsize=10,
        autocommit=True
    )

async def get_db_connection():
    pool = await get_db_pool()
    return await pool.acquire() 