from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import database, engine
from src.models import metadata
from src.routes import recipes, fridge, favorites, ingredients


@asynccontextmanager
async def lifespan(app: FastAPI):
    metadata.create_all(engine)
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(
    title="食譜管理 API",
    description="提供食譜查詢、冰箱管理、收藏功能的後端 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipes.router, prefix="/api/recipes", tags=["食譜"])
app.include_router(fridge.router, prefix="/api/fridge", tags=["冰箱"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["收藏"])
app.include_router(ingredients.router, prefix="/api/ingredients", tags=["食材"])


@app.get("/", tags=["健康檢查"])
async def root():
    return {"message": "食譜 API 運作中", "docs": "/docs"}


@app.get("/health", tags=["健康檢查"])
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
