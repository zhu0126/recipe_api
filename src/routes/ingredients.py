from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from src.database import database
from src.services import ingredient_service
from src.schemas import IngredientCreate

router = APIRouter()


@router.get("/", summary="取得所有可用食材")
async def list_ingredients(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    return await ingredient_service.list_ingredients(database, category, page, page_size)


@router.get("/search", summary="食材模糊查詢")
async def search_ingredients(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
):
    return await ingredient_service.search_ingredients(database, q, limit)


@router.post("/", summary="新增食材到系統", status_code=201)
async def create_ingredient(body: IngredientCreate):
    result = await ingredient_service.create_ingredient(database, body.name, body.category, body.unit)
    if not result:
        raise HTTPException(status_code=409, detail=f"食材「{body.name}」已存在")
    return result
