from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.post("/reset")
def reset_db():
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("SELECT delete_database()"))
        connection.execute(sqlalchemy.text("SELECT create_database()"))

@router.post("/load")
def load_data():
    with db.engine.being() as connection:
        connection.execute(sqlalchemy.text("SELECT load_database()"))
            