from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional

from src.database import database
from src.services import recipe_service

router = APIRouter()


@router.get("/home", summary="首頁推薦與熱門食譜")
async def home_recipes(limit: int = Query(10, ge=1, le=50)):
    return await recipe_service.get_home_recipes(database, limit)


@router.get("/search", summary="食譜名稱關鍵字搜尋")
async def search_recipes(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    return await recipe_service.search_recipes(database, q, page, page_size)


@router.get("/by-ingredients", summary="輸入食材查詢食譜")
async def recipes_by_ingredients(
    ingredient_names: str = Query(..., description="逗號分隔，如：雞蛋,番茄"),
    match_all: bool = Query(False),
):
    names = [n.strip() for n in ingredient_names.split(",") if n.strip()]
    return await recipe_service.get_recipes_by_ingredients(database, names, match_all)


@router.get("/advanced", summary="食譜進階篩選與排序")
async def advanced_filter(
    keyword: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    max_time: Optional[int] = Query(None),
    tags: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    return await recipe_service.advanced_filter(
        database, keyword, cuisine, difficulty, max_time, tags, sort_by, order, page, page_size
    )


@router.get("/", summary="查看全部食譜")
async def list_recipes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    from src.models import recipes
    offset = (page - 1) * page_size
    rows = await database.fetch_all(
        recipes.select().order_by(recipes.c.created_at.desc()).offset(offset).limit(page_size)
    )
    return {"page": page, "page_size": page_size, "results": [dict(r) for r in rows]}


@router.get("/{recipe_id}", summary="取得單一食譜詳細資訊")
async def get_recipe(recipe_id: int):
    result = await recipe_service.get_recipe_detail(database, recipe_id)
    if not result:
        raise HTTPException(status_code=404, detail="食譜不存在")
    return result
