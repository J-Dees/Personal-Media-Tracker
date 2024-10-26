from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/user_functions",
    tags=["user functions"],
)

@router.post("user/create")
def create_new_user(name):
    with db.engine.begin() as connection:
        user_id = connection.execute(sqlalchemy.text("""INSERT INTO users
                                                    VALUES (:name)
                                                    RETURNING id"""), {'name': name}).scalar_one()
    return {
            "user_id": user_id
            }

@router.get("user/login")
def login_user():
    # verify that the username exists and return a successful login message, allow access to catalogs for that user
    return "OK"

@router.delete("user/{user_id}")
def delete_user():
    # remove user with passed id from user table
    return "OK"