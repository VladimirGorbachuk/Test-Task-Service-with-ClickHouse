import os

import asyncpg


async def create_connection_pool():
    return await asyncpg.create_pool(
            os.environ["DATABASE_URL"],
            min_size=1,
            max_size=10,
            timeout=30
        )