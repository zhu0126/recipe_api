from datetime import datetime
from src.models import favorites, recipes

USER_ID = 1


async def get_favorites(db, page: int, page_size: int) -> dict:
    offset = (page - 1) * page_size
    query = (
        favorites.join(recipes, favorites.c.recipe_id == recipes.c.id)
        .select()
        .where(favorites.c.user_id == USER_ID)
        .order_by(favorites.c.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = await db.fetch_all(query)
    return {
        "page": page,
        "page_size": page_size,
        "results": [
            {
                "favorite_id": r["id"],
                "recipe_id": r["recipe_id"],
                "recipe_name": r["name"],
                "description": r["description"],
                "cooking_time": r["cooking_time"],
                "difficulty": r["difficulty"],
                "image_url": r["image_url"],
                "favorited_at": r["created_at"],
            }
            for r in rows
        ],
    }


async def toggle_favorite(db, recipe_id: int) -> dict:
    recipe = await db.fetch_one(recipes.select().where(recipes.c.id == recipe_id))
    if not recipe:
        return None

    existing = await db.fetch_one(
        favorites.select().where(
            (favorites.c.user_id == USER_ID) & (favorites.c.recipe_id == recipe_id)
        )
    )

    if existing:
        await db.execute(favorites.delete().where(favorites.c.id == existing["id"]))
        await db.execute(
            recipes.update().where(recipes.c.id == recipe_id)
            .values(like_count=max(0, recipe["like_count"] - 1))
        )
        return {"recipe_id": recipe_id, "is_favorited": False, "message": "已取消收藏"}

    await db.execute(
        favorites.insert().values(user_id=USER_ID, recipe_id=recipe_id, created_at=datetime.utcnow())
    )
    await db.execute(
        recipes.update().where(recipes.c.id == recipe_id)
        .values(like_count=recipe["like_count"] + 1)
    )
    return {"recipe_id": recipe_id, "is_favorited": True, "message": "已加入收藏"}
