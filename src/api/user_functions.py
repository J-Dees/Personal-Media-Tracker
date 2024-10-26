from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/user_functions",
    tags=["user functions"],
)

@router.post("user/create", status_code=201)
def create_new_user(name):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""INSERT INTO users (name)
                                              VALUES (:name)"""), {'name': name})
    return "OK"

@router.get("user/login")
def login_user(name):
    with db.engine.begin() as connection:
        user_id = connection.execute(sqlalchemy.text("""SELECT id
                                                        FROM users
                                                        WHERE name = :name"""), {'name' : name}).scalar_one()
    return {
            "user_id": user_id
            }

@router.delete("user/{user_id}", status_code=204)
def delete_user(user_id):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""DELETE FROM users
                                              WHERE id = :user_id"""), {'user_id': user_id})
    # TEST LATER to make sure it cascades
    return "OK"