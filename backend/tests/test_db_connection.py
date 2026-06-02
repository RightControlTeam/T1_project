# test_db_connection.py
import asyncio
import asyncpg

async def test_connection():
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            database='postgres',
            host='localhost',
            port=5432
        )
        print("Успешное подключение к PostgreSQL!")
        await conn.close()
    except Exception as e:
        print(f"Ошибка подключения: {e}")

asyncio.run(test_connection())