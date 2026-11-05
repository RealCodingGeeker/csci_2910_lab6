from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import artworks
from app.scripts.populate_db import populate


@asynccontextmanager
async def lifespan(app: FastAPI):
    populate()
    yield


def start():
    """Launched with `uv run dev`"""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


app = FastAPI(
    title="Art API",
    description="A REST API for famous works of art.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(artworks.router)
