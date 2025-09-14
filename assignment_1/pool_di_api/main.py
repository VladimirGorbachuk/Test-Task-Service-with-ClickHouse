from contextlib import asynccontextmanager
import os
from typing import Annotated

import asyncpg
import uvicorn
from fastapi import APIRouter, FastAPI, Depends

from pool_di_api.di import set_dependency_injection
from pool_di_api.interfaces import ConnectionProtocol
from pool_di_api.psql_pool import create_connection_pool


router = APIRouter(prefix="/api")

@router.get("/db_version")
async def get_db_version(conn: ConnectionProtocol = Depends()):
    return await conn.fetchval(query="SELECT version()")



@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.connection_pool = await create_connection_pool()
    yield
    await app.state.connection_pool.close()


def create_app() -> FastAPI:
    app = FastAPI(title="some_firm_which_gave_test_assignment", lifespan=lifespan)
    set_dependency_injection(app)
    app.include_router(router)
    return app


def run_app():
    uvicorn.run(create_app, factory=True)
