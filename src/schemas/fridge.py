from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FridgeItemIn(BaseModel):
    ingredient_name: str = Field(..., example="番茄")
    quantity: Optional[float] = Field(1, example=3)
    unit: Optional[str] = Field(None, example="顆")
    expired_at: Optional[datetime] = None


class FridgeItemUpdate(BaseModel):
    quantity: float = Field(..., example=5)
    unit: Optional[str] = None
    expired_at: Optional[datetime] = None


class FridgeBatchIn(BaseModel):
    items: List[FridgeItemIn]


class FridgeItemOut(BaseModel):
    id: int
    ingredient_id: int
    ingredient_name: str
    category: Optional[str]
    quantity: float
    unit: Optional[str]
    expired_at: Optional[datetime]
    added_at: datetime
