from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RecipeIngredientOut(BaseModel):
    ingredient_id: int
    name: str
    quantity: Optional[float]
    unit: Optional[str]
    note: Optional[str]


class RecipeBase(BaseModel):
    name: str = Field(..., example="番茄炒蛋")
    description: Optional[str] = None
    cooking_time: Optional[int] = Field(None, example=20, description="分鐘")
    difficulty: Optional[str] = Field(None, example="簡單")
    cuisine: Optional[str] = Field(None, example="中式")
    tags: Optional[str] = Field(None, example="快炒,家常")
    image_url: Optional[str] = None


class RecipeOut(RecipeBase):
    id: int
    view_count: int
    like_count: int
    created_at: datetime
    is_favorited: Optional[bool] = False

    class Config:
        from_attributes = True


class RecipeDetailOut(RecipeOut):
    steps: Optional[str] = None
    ingredients: List[RecipeIngredientOut] = []
