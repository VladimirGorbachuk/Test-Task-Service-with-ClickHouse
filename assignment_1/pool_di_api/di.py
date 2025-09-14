from collections.abc import Generator

import asyncpg
from fastapi import Depends, FastAPI

from pool_di_api.interfaces import ConnectionPoolProtocol, ConnectionProtocol



def get_connection_pool(app: FastAPI) -> Generator[asyncpg.Pool, None, None]:
    if not hasattr(app.state, "connection_pool"):
        raise ValueError("Initialize connection pool in lifespan")
    return app.state.connection_pool


async def get_connection(
    connection_pool: ConnectionPoolProtocol = Depends(),
) -> asyncpg.Connection:
    async with connection_pool.acquire() as connection:
        try:
            yield connection
        finally:
            connection.close()


def set_dependency_injection(app: FastAPI) -> None:
    app.dependency_overrides.update(
        {
            ConnectionPoolProtocol: lambda: get_connection_pool(app),
            ConnectionProtocol: get_connection,
        }
    )
