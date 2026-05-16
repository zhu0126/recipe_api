import sqlalchemy
from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Float,
    Text, DateTime, ForeignKey, UniqueConstraint
)
from datetime import datetime

metadata = MetaData()

ingredients = Table(
    "ingredients", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False, unique=True),
    Column("category", String(50)),
    Column("unit", String(20), default="份"),
    Column("created_at", DateTime, default=datetime.utcnow),
)

recipes = Table(
    "recipes", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(200), nullable=False),
    Column("description", Text),
    Column("steps", Text),
    Column("cooking_time", Integer),
    Column("difficulty", String(20)),
    Column("cuisine", String(50)),
    Column("tags", String(200)),
    Column("image_url", String(500)),
    Column("view_count", Integer, default=0),
    Column("like_count", Integer, default=0),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

recipe_ingredients = Table(
    "recipe_ingredients", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("recipe_id", Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False),
    Column("quantity", Float),
    Column("unit", String(20)),
    Column("note", String(100)),
    UniqueConstraint("recipe_id", "ingredient_id"),
)

fridge_items = Table(
    "fridge_items", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, default=1),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False),
    Column("quantity", Float, default=1),
    Column("unit", String(20)),
    Column("expired_at", DateTime, nullable=True),
    Column("added_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
    UniqueConstraint("user_id", "ingredient_id"),
)

favorites = Table(
    "favorites", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, default=1),
    Column("recipe_id", Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
    UniqueConstraint("user_id", "recipe_id"),
)
