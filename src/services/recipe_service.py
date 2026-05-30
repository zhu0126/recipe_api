import json
import sqlalchemy as sa
from typing import Optional
from collections import Counter

from src.models import recipes, recipe_ingredients, ingredients, user_recipes, recipe_label, recipe_cook_methods

USER_ID = "001" 

# 注釋：view_count 和 like_count 列不存在於 tables.py 中
"""
async def get_home_recipes(db, limit: int) -> dict:
    popular = await db.fetch_all(
        recipes.select().order_by(recipes.c.view_count.desc()).limit(limit)
    )
    recommended = await db.fetch_all(
        recipes.select().order_by(recipes.c.like_count.desc()).limit(limit)
    )
    return {
        "popular": [dict(r) for r in popular],
        "recommended": [dict(r) for r in recommended],
    }
"""


# 注釋：name 列和 view_count 列不存在於 tables.py 中
"""
async def search_recipes(db, q: str, page: int, page_size: int) -> dict:
    offset = (page - 1) * page_size
    rows = await db.fetch_all(
        recipes.select()
        .where(recipes.c.name.ilike(f"%{q}%"))
        .order_by(recipes.c.view_count.desc())
        .offset(offset)
        .limit(page_size)
    )
    total = await db.fetch_val(
        sa.select(sa.func.count()).select_from(recipes).where(recipes.c.name.ilike(f"%{q}%"))
    )
    return {"total": total, "page": page, "page_size": page_size, "results": [dict(r) for r in rows]}
"""


async def get_recipes_by_ingredients(db, names: list, match_all: bool) -> dict:
    ing_rows = await db.fetch_all(
        ingredients.select().where(ingredients.c.name.in_(names))
    )
    ing_ids = [r["ingredient_id"] for r in ing_rows]
    if not ing_ids:
        return {"recipes": [], "message": "找不到對應食材"}

    ri_rows = await db.fetch_all(
        recipe_ingredients.select().where(recipe_ingredients.c.ingredient_id.in_(ing_ids))
    )
    id_counts = Counter(r["recipe_id"] for r in ri_rows)

    matched_ids = (
        [rid for rid, cnt in id_counts.items() if cnt >= len(ing_ids)]
        if match_all else list(id_counts.keys())
    )
    if not matched_ids:
        return {"recipes": [], "message": "沒有符合條件的食譜"}

    rows = await db.fetch_all(
        recipes.select().where(recipes.c.recipe_id.in_(matched_ids))
    )
    results = sorted(
        [dict(r) | {"match_count": id_counts[r["recipe_id"]]} for r in rows],
        key=lambda x: x["match_count"],
        reverse=True,
    )
    return {"total": len(results), "recipes": results}


# 注釋：name, cuisine, cooking_time, tags 列不存在於 tables.py 中，參數簽名與路由不匹配
"""
async def advanced_filter(db, keyword, cuisine, difficulty, max_time, tags, sort_by, order, page, page_size) -> dict:
    offset = (page - 1) * page_size
    stmt = recipes.select()

    if keyword:
        stmt = stmt.where(recipes.c.name.ilike(f"%{keyword}%"))
    if cuisine:
        stmt = stmt.where(recipes.c.cuisine == cuisine)
    if difficulty:
        stmt = stmt.where(recipes.c.difficulty == difficulty)
    if max_time:
        stmt = stmt.where(recipes.c.cooking_time <= max_time)
    if tags:
        for tag in tags.split(","):
            stmt = stmt.where(recipes.c.tags.ilike(f"%{tag.strip()}%"))

    allowed_sort = {"cook_time", "servings", "title"}
    sort_col = getattr(recipes.c, sort_by) if sort_by in allowed_sort else recipes.c.recipe_id
    stmt = stmt.order_by(sort_col.asc() if order == "asc" else sort_col.desc())
    stmt = stmt.offset(offset).limit(page_size)

    rows = await db.fetch_all(stmt)
    return {"page": page, "page_size": page_size, "results": [dict(r) for r in rows]}
"""


async def get_recipe_detail(db, recipe_id: int) -> dict:
    row = await db.fetch_one(recipes.select().where(recipes.c.recipe_id == recipe_id))
    if not row:
        return None

    # await db.execute(
    #     recipes.update().where(recipes.c.id == recipe_id).values(view_count=row["view_count"] + 1)
    # )

    ing_query = (
        recipe_ingredients.join(ingredients, recipe_ingredients.c.ingredient_id == ingredients.c.ingredient_id)
        .select()
        .where(recipe_ingredients.c.recipe_id == recipe_id)
    )
    ing_rows = await db.fetch_all(ing_query)
    ing_list = [
        {
            "ingredient_id": r["ingredient_id"],
            "name": r["name"],
            "amount": r["amount"],
            "unit": r["unit"],
        }
        for r in ing_rows
    ]

    # 標籤
    label_rows = await db.fetch_all(
        recipe_label.select().where(recipe_label.c.recipe_id == recipe_id)
    )
    labels = [r["label"] for r in label_rows]

    # 烹飪方式
    method_rows = await db.fetch_all(
        recipe_cook_methods.select().where(recipe_cook_methods.c.recipe_id == recipe_id)
    )
    cook_methods = [r["cook_methods"] for r in method_rows]

    fav_row = await db.fetch_one(
        user_recipes.select().where((user_recipes.c.recipe_id == recipe_id) & (user_recipes.c.user_id == USER_ID))
    )

    result = dict(row)
    result["ingredients"] = ing_list
    result["labels"] = labels
    result["cook_methods"] = cook_methods
    result["is_favorited"] = fav_row is not None

    return result
