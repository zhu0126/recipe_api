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
        database, item.ingredient_name, item.quantity, item.unit, item.expired_at
    )


@router.post("/batch", summary="批次新增食材", status_code=201)
async def batch_add(batch: FridgeBatchIn):
    return await fridge_service.batch_add(database, batch.items)


@router.put("/{item_id}", summary="修改冰箱食材數量")
async def update_item(item_id: int, update: FridgeItemUpdate):
    result = await fridge_service.update_item(
        database, item_id, update.quantity, update.unit, update.expired_at
    )
    if not result:
        raise HTTPException(status_code=404, detail="冰箱中找不到此食材")
    return result


@router.delete("/{item_id}", summary="從冰箱移除食材")
async def remove_item(item_id: int):
    success = await fridge_service.remove_item(database, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="冰箱中找不到此食材")
    return {"message": "已移除食材", "id": item_id}


@router.delete("/", summary="一鍵清空冰箱")
async def clear_fridge():
    return await fridge_service.clear_fridge(database)
