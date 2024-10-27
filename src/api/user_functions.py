from fastapi import APIRouter, Response, status
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/user",
    tags=["user functions"],
)

@router.post("/create")
def create_new_user(name, response: Response):
    '''Creates a new user with the passed name and assigns a unique ID. If the user name is taken, the new user is informed to pick a different name.'''
    with db.engine.begin() as connection:
        try:
            connection.execute(sqlalchemy.text("""INSERT INTO users (name)
                                                VALUES (:name)"""), {'name': name})
            response.status_code = status.HTTP_201_CREATED
            return "OK"
        except:
            response.status_code = status.HTTP_403_FORBIDDEN
            return "Username already taken, please choose a different name."
    

@router.get("/login")
def login_user(name, response: Response):
    '''Allows the user to login with their username. If no such user exists, a message is sent to inform that no user exists by that name.'''
    with db.engine.begin() as connection:
        try:
            user_id = connection.execute(sqlalchemy.text("""SELECT id
                                                            FROM users
                                                            WHERE name = :name"""), {'name' : name}).scalar_one()
            return {
                    "user_id": user_id
                    }
        except:
            response.status_code = status.HTTP_404_NOT_FOUND
            return "User with provided username not found."

@router.delete("/{user_id}")
def delete_user(user_id):
    '''Deletes a user account. This will remove all traces of the user including catalogs, entries, and followers.'''
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""DELETE FROM users
                                              WHERE id = :user_id"""), {'user_id': user_id})
    # TEST LATER to make sure it cascades
    return "OK"