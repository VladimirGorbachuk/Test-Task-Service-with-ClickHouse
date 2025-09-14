from collections.abc import Generator
from typing import Protocol

import asyncpg


class ConnectionPoolProtocol(Protocol):
    async def acquire(self) -> Generator[asyncpg.Connection, None, None]:
        raise NotImplementedError()
    
    async def release(self, connection: asyncpg.Connection) -> None:
        raise NotImplementedError()
    
    async def close(self) -> None:
        raise NotImplementedError()
    
    async def __aenter__(self):
        raise NotImplementedError()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()


class ConnectionProtocol(Protocol):
    async def execute(self, query: str, *args, timeout: float = None) -> str:
        raise NotImplementedError()

    async def fetchval(self, query: str, *args, timeout: float = None) -> str:
        raise NotImplementedError()
    
    async def close(self) -> None:
        raise NotImplementedError()
