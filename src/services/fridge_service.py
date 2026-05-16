from datetime import datetime
from typing import Optional

from src.models import fridge_items, ingredients

USER_ID = 1


async def _get_or_create_ingredient(db, name: str, unit: Optional[str] = None) -> int:
    row = await db.fetch_one(ingredients.select().where(ingredients.c.name == name))
    if row:
        return row["id"]
    return await db.execute(ingredients.insert().values(name=name, unit=unit or "份"))


async def get_fridge(db) -> list:
    query = (
        fridge_items.join(ingredients, fridge_items.c.ingredient_id == ingredients.c.id)
        .select()
        .where(fridge_items.c.user_id == USER_ID)
        .order_by(fridge_items.c.added_at.desc())
    )
    rows = await db.fetch_all(query)
    return [
        {
            "id": r["id"],
            "ingredient_id": r["ingredient_id"],
            "ingredient_name": r["name"],
            "category": r["category"],
            "quantity": r["quantity"],
            "unit": r["unit"],
            "expired_at": r["expired_at"],
            "added_at": r["added_at"],
        }
        for r in rows
    ]


async def add_item(db, ingredient_name: str, quantity: float, unit: Optional[str], expired_at) -> dict:
    ing_id = await _get_or_create_ingredient(db, ingredient_name, unit)
    existing = await db.fetch_one(
        fridge_items.select().where(
            (fridge_items.c.user_id == USER_ID) & (fridge_items.c.ingredient_id == ing_id)
        )
    )
    if existing:
        new_qty = existing["quantity"] + (quantity or 1)
        await db.execute(
            fridge_items.update()
            .where(fridge_items.c.id == existing["id"])
            .values(quantity=new_qty, updated_at=datetime.utcnow())
        )
        return {"message": f"已更新 {ingredient_name} 數量為 {new_qty}", "action": "updated"}

    fid = await db.execute(
        fridge_items.insert().values(
            user_id=USER_ID, ingredient_id=ing_id,
            quantity=quantity or 1, unit=unit,
            expired_at=expired_at,
            added_at=datetime.utcnow(), updated_at=datetime.utcnow(),
        )
    )
    return {"message": f"已新增 {ingredient_name} 到冰箱", "id": fid, "action": "created"}


async def batch_add(db, items: list) -> dict:
    results = []
    for item in items:
        result = await add_item(db, item.ingredient_name, item.quantity, item.unit, item.expired_at)
        results.append({"name": item.ingredient_name, **result})
    return {"message": f"批次處理 {len(results)} 項食材", "results": results}


async def update_item(db, item_id: int, quantity: float, unit: Optional[str], expired_at) -> dict:
    existing = await db.fetch_one(
        fridge_items.select().where(
            (fridge_items.c.id == item_id) & (fridge_items.c.user_id == USER_ID)
        )
    )
    if not existing:
        return None
    values = {"quantity": quantity, "updated_at": datetime.utcnow()}
    if unit is not None:
        values["unit"] = unit
    if expired_at is not None:
        values["expired_at"] = expired_at
    await db.execute(fridge_items.update().where(fridge_items.c.id == item_id).values(**values))
    return {"message": "更新成功", "id": item_id, "quantity": quantity}


async def remove_item(db, item_id: int) -> bool:
    existing = await db.fetch_one(
        fridge_items.select().where(
            (fridge_items.c.id == item_id) & (fridge_items.c.user_id == USER_ID)
        )
    )
    if not existing:
        return False
    await db.execute(fridge_items.delete().where(fridge_items.c.id == item_id))
    return True


async def clear_fridge(db) -> dict:
    await db.execute(fridge_items.delete().where(fridge_items.c.user_id == USER_ID))
    return {"message": "冰箱已清空"}
