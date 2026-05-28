from fastapi import APIRouter, HTTPException

from src.database import database
from src.services import fridge_service
from src.schemas import FridgeItemIn, FridgeItemUpdate, FridgeBatchIn

router = APIRouter()


@router.get("/", summary="顯示冰箱擁有的食材")
async def get_fridge():
    return await fridge_service.get_fridge(database)


@router.post("/", summary="新增食材到冰箱", status_code=201)
async def add_to_fridge(item: FridgeItemIn):
    return await fridge_service.add_item(
        database, item.ingredient_name, item.amount,
        item.unit, item.expiration_date, item.storage_location
    )


@router.post("/batch", summary="批次新增食材", status_code=201)
async def batch_add(batch: FridgeBatchIn):
    return await fridge_service.batch_add(database, batch.items)


@router.put("/{ingredient_id}", summary="修改冰箱食材數量")
async def update_item(ingredient_id: str, update: FridgeItemUpdate):
    result = await fridge_service.update_item(
        database, ingredient_id, update.amount,
        update.unit, update.expiration_date, update.storage_location
    )
    if not result:
        raise HTTPException(status_code=404, detail="冰箱中找不到此食材")
    return result


@router.delete("/{ingredient_id}", summary="從冰箱移除食材")
async def remove_item(ingredient_id: str):
    success = await fridge_service.remove_item(database, ingredient_id)
    if not success:
        raise HTTPException(status_code=404, detail="冰箱中找不到此食材")
    return {"message": "已移除食材", "ingredient_id": ingredient_id}


@router.delete("/", summary="一鍵清空冰箱")
async def clear_fridge():
    return await fridge_service.clear_fridge(database)
