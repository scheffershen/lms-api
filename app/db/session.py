from aiomysql import create_pool
from app.core.config import settings

async def get_db_pool():
    # Debug print
    print("Database Settings:")
    print(f"MYSQL_HOST: {settings.MYSQL_HOST}")
    print(f"MYSQL_USER: {settings.MYSQL_USER}")
    print(f"MYSQL_PASSWORD: {settings.MYSQL_PASSWORD}")
    print(f"MYSQL_DATABASE: {settings.MYSQL_DATABASE}")
    
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