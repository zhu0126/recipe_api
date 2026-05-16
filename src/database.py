import databases
import sqlalchemy
from src.config import settings

database = databases.Database(settings.DATABASE_URL)
engine = sqlalchemy.create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
