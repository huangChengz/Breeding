import asyncio
import asyncpg

async def update_db():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='123456',
        database='breeding'
    )
    await conn.execute('ALTER TABLE node_references ALTER COLUMN ref_type_id DROP NOT NULL')
    print('Done')
    await conn.close()

asyncio.run(update_db())
