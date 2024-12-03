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
    '''Creates a new user with the passed name and assigns a unique ID.\\
    The username must be a unique name.'''
    with db.engine.begin() as connection:
        try:
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO users (name)
                VALUES (:name)
                """), {'name': name})
            response.status_code = status.HTTP_201_CREATED
            return {"response": "User created"}
        except:
            response.status_code = status.HTTP_409_CONFLICT
            return {"error": "Username already taken, please choose a different name."}
    
class asc_desc(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("")
def get_users(response: Response,
              page: int = 1, 
              name: str = "",
              direction: asc_desc = asc_desc.asc):
    """Lists all users fitting the query parameters.
        - page: The page of results to return.
        - name: A String that each name returned must contain.
        - direction: The sort order of the results in either `asc` or `desc` order."""
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

    return db.execute_search(stats_statement, content_statement, page, response)

@router.get("/{user_name}")
def login_user(user_name, response: Response):
    '''Allows the user to login with their username. 
        - The username must exist.
        - The returned user_id will be used as authentication to modify anything related to the user.'''
    with db.engine.begin() as connection:
        try:
            user_id = connection.execute(sqlalchemy.text(
                """
                SELECT id
                FROM users
                WHERE name = :name
                """), {'name' : user_name}).scalar_one()
            return {
                    "user_id": user_id
                    }
        except:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"error": "User with provided username not found."}

@router.delete("/{user_id}")
def delete_user(user_id, response: Response):
    '''Deletes a user account. 
        - This will remove all traces of the user including catalogs, entries, and followers.'''

    with db.engine.begin() as connection:
        results = connection.execute(sqlalchemy.text(
            """
            DELETE FROM users
            WHERE id = :user_id 
            """), {'user_id': user_id})
        if results.rowcount != 1:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"error": "Invalid user id."}
    response.status_code = status.HTTP_206_PARTIAL_CONTENT
    return {"response": "Successfully deleted user account and all references."}
    