import json
import sqlalchemy as sa
from typing import Optional
from collections import Counter

from src.models import recipes, recipe_ingredients, ingredients, user_recipes, recipe_label, recipe_cook_methods

USER_ID = "001" 

async def get_home_recipes(db, limit: int) -> dict:
    popular = await db.fetch_all(
        recipes.select()
        .order_by(recipes.c.recipe_id.desc())
        .limit(limit)
    )

    recommended = await db.fetch_all(
        recipes.select()
        .order_by(recipes.c.recipe_id.asc())
        .limit(limit)
    )

    return {
        "popular": [dict(r) for r in popular],
        "recommended": [dict(r) for r in recommended],
    }

async def search_recipes(db, q: str, page: int, page_size: int) -> dict:
    offset = (page - 1) * page_size

    condition = recipes.c.title.ilike(f"%{q}%")

    rows = await db.fetch_all(
        recipes.select()
        .where(condition)
        .order_by(recipes.c.recipe_id)
        .offset(offset)
        .limit(page_size)
    )

    total = await db.fetch_val(
        sa.select(sa.func.count())
        .select_from(recipes)
        .where(condition)
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": [dict(r) for r in rows],
    }

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

async def advanced_filter(
    db,
    keyword,
    label,
    difficulty,
    max_time,
    is_vegetarian,
    sort_by,
    order,
    page,
    page_size
) -> dict:
    offset = (page - 1) * page_size
    stmt = recipes.select()

    if keyword:
        stmt = stmt.where(recipes.c.title.ilike(f"%{keyword}%"))

    if difficulty:
        stmt = stmt.where(recipes.c.difficulty == difficulty)

    if max_time:
        stmt = stmt.where(recipes.c.cook_time <= max_time)

    if is_vegetarian is not None:
        stmt = stmt.where(recipes.c.is_vegetarian == is_vegetarian)

    allowed_sort = {
        "recipe_id": recipes.c.recipe_id,
        "cook_time": recipes.c.cook_time,
        "servings": recipes.c.servings,
        "title": recipes.c.title,
    }

    sort_col = allowed_sort.get(sort_by, recipes.c.recipe_id)

    if order == "desc":
        stmt = stmt.order_by(sort_col.desc())
    else:
        stmt = stmt.order_by(sort_col.asc())

    rows = await db.fetch_all(
        stmt.offset(offset).limit(page_size)
    )

    return {
        "page": page,
        "page_size": page_size,
        "results": [dict(r) for r in rows],
    }

async def get_recipe_detail(db, recipe_id: int) -> dict | None:
    row = await db.fetch_one(
        recipes.select().where(recipes.c.recipe_id == recipe_id)
    )

    if not row:
        return None

    ing_query = (
        recipe_ingredients
        .join(ingredients, recipe_ingredients.c.ingredient_id == ingredients.c.ingredient_id)
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

    label_rows = await db.fetch_all(
        recipe_label.select().where(recipe_label.c.recipe_id == recipe_id)
    )
    labels = [r["label"] for r in label_rows]

    method_rows = await db.fetch_all(
        recipe_cook_methods.select().where(recipe_cook_methods.c.recipe_id == recipe_id)
    )
    cook_methods = [r["cook_methods"] for r in method_rows]

    fav_row = await db.fetch_one(
        user_recipes.select().where(
            (user_recipes.c.recipe_id == recipe_id) &
            (user_recipes.c.user_id == USER_ID)
        )
    )

    result = dict(row)
    result["ingredients"] = ing_list
    result["labels"] = labels
    result["cook_methods"] = cook_methods
    result["is_favorited"] = fav_row is not None

    return result