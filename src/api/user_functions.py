from enum import Enum
from fastapi import APIRouter, Response, status

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["user functions"],
)

@router.post("")
def create_new_user(name, response: Response):
    '''Creates a new user with the passed name and assigns a unique ID. If the user name is taken, the new user is informed to pick a different name.'''
    with db.engine.begin() as connection:
        try:
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO users (name)
                VALUES (:name)
                """), {'name': name})
            response.status_code = status.HTTP_201_CREATED
            return "OK"
        except:
            response.status_code = status.HTTP_409_CONFLICT
            return "Username already taken, please choose a different name."
    
class asc_desc(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/search")
def get_users(page: int = 1, 
              name: str = "",
              direction: asc_desc = asc_desc.asc):
    """Lists all users"""
    stats_statement = (
        sqlalchemy.select(
            sqlalchemy.func.count(db.users.c.id).label("total_rows"))
        .select_from(db.users)
        .where(db.users.c.name.ilike(f"%{name}%"))
    )
    #Statement for gathering the primary content returned.
    content_statement = (
        sqlalchemy.select(
            db.users.c.name)
        .select_from(db.users)
        .where(db.users.c.name.ilike(f"%{name}%"))
        .limit(db.MAX_PER_PAGE).offset(db.MAX_PER_PAGE*(page-1))
    )

    #Append proper order_by to the query.
    if (direction == "desc"):
        content_statement = content_statement.order_by(sqlalchemy.desc(db.users.c.name))
    else:
        content_statement = content_statement.order_by(db.users.c.name)

    return db.execute_search(stats_statement, content_statement, page)

@router.get("")
def login_user(name, response: Response):
    '''Allows the user to login with their username. If no such user exists, a message is sent to inform that no user exists by that name.'''
    with db.engine.begin() as connection:
        try:
            user_id = connection.execute(sqlalchemy.text(
                """
                SELECT id
                FROM users
                WHERE name = :name
                """), {'name' : name}).scalar_one()
            return {
                    "user_id": user_id
                    }
        except:
            response.status_code = status.HTTP_404_NOT_FOUND
            return "User with provided username not found."

@router.delete("")
def delete_user(user_id, response: Response):
    '''Deletes a user account. This will remove all traces of the user including catalogs, entries, and followers.'''
    # API Spec notes that user will receive a warning prior to deletion
    try:
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(
                """
                DELETE FROM users
                WHERE id = :user_id
                """), {'user_id': user_id})
        # TEST LATER to make sure it cascades
        response.status_code = status.HTTP_204_NO_CONTENT
        return "Successfully deleted user account and all references."
    except:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "Invalid user id."