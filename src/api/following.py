from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/user",
    tags=["following"],
)

@router.post("/{user_id}/social")
def add_follower(user_id: int, user_name: str):
    """ follow a user """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO social (user_id, follower_id)
            VALUES(
                (
                    SELECT id
                    FROM users
                    WHERE users.name = :user_name
                ),
                :user_id
            )
            """
        ),
            {
                'user_name': user_name,
                'user_id': user_id
            }
        )
    return "OK"

@router.get("/{user_id}/social/search")
def search_follower(user_id: int):
    """ searches through a user's followers based on query """
    with db.engine.begin() as connection:
        followers = connection.execute(sqlalchemy.text(
            """
            SELECT users.name
            FROM social
            JOIN users ON users.id = social.follower_id
            WHERE social.user_id = :user_id
            ORDER BY users.name ASC
            """
        ),
            {
                'user_id': user_id
            }
        ).mappings().fetchall()

    return followers

@router.delete("/{user_id}/social/{follower_id}")
def remove_follower(user_id: int, follower_name: str):
    """ DELETE FROM social the user_id/follower_id pair """
    with db.engine.begin() as connection:
        try:
            result = connection.execute(sqlalchemy.text(
                """
                DELETE FROM social
                WHERE follower_id = (
                    SELECT follower_id
                    FROM users
                    WHERE users.name = :follower_name
                    )
                    and social.user_id = :user_id;

                SELECT user_id, follower_id
                FROM social
                WHERE user_id = :user_id
                AND follower_id = (
                    SELECT follower_id
                    FROM users
                    WHERE users.name = :follower_name
                )
                """
            ),
                {
                    'follower_name': follower_name,
                    'user_id': user_id,
                    'follower_name': follower_name,
                    'user_id': user_id
                }
            ).first()
        except ():
            return False

    if result != None:
        print("row not deleted")
        return False
    else:
        return True

@router.get("/{user_id}/social/{follower_name}/catalogs")
def view_follower_catalogs(user_id:int , follower_name: str):
    """ view a specified follower's catalogs """

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT user_id, follower_id
            FROM social
            JOIN users ON users.id = social.follower_id
            WHERE users.name = :follower_name
            AND user_id = :user_id
            """
        ), 
            {
                'follower_name': follower_name,
                'user_id': user_id
            }
        ).first()

    if result == None:
        print(f"User is not following {follower_name}")
        return []

    with db.engine.begin() as connection:
        catalogs = connection.execute(sqlalchemy.text(
            """
            SELECT catalogs.name, catalogs.type
            FROM catalogs
            JOIN users ON users.id = catalogs.user_id
            WHERE users.name = :follower_name
            AND catalogs.private = FALSE
            """
        ), 
            {
                'follower_name': follower_name
            }
        ).mappings().fetchall()

    return catalogs

@router.get("/{user_id}/social/{follower_name}/catalogs/{catalog}/recommendations")
def get_recommended(user_id: int, follower_name: str, catalog: str):
    """ view all catalog entries that are flagged as recommended in a given follower catalog """
    # this is probably something we can implement into a user's own catalogs as well

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT user_id, follower_id
            FROM social
            JOIN users ON users.id = social.follower_id
            WHERE users.name = :follower_name
            AND user_id = :user_id
            """
        ), 
            {
                'follower_name': follower_name,
                'user_id': user_id
            }
        ).first()

    if result == None:
        print(f"User is not following {follower_name}")
        return []

    with db.engine.begin() as connection:
        catalog_type = connection.execute(sqlalchemy.text(
            """
            SELECT type
            FROM catalogs
            JOIN users ON users.id = catalogs.user_id
            WHERE users.name = :follower_name
            """
        ),{'follower_name': follower_name}).scalar()


    with db.engine.begin() as connection:
        match catalog_type:
            case 'games':
                recommended_entries = connection.execute(sqlalchemy.text(
                    """
                    SELECT *
                    FROM catalogs
                    JOIN users ON users.id = catalogs.user_id
                    JOIN entries ON entries.catalog_id = catalogs.id
                    JOIN game_entry on game_entry.entry_id = entries.id
                    """
                )).mappings().fetchall()
            case 'movies':
                recommended_entries = connection.execute(sqlalchemy.text(
                    """
                    SELECT *
                    FROM catalogs
                    JOIN users ON users.id = catalogs.user_id
                    JOIN entries ON entries.catalog_id = catalogs.id
                    JOIN movies_entry on movies_entry.entry_id = entries.id
                    """
                )).mappings().fetchall()
            case 'books':
                recommended_entries = connection.execute(sqlalchemy.text(
                    """
                    SELECT *
                    FROM catalogs
                    JOIN users ON users.id = catalogs.user_id
                    JOIN entries ON entries.catalog_id = catalogs.id
                    JOIN books_entry on books_entry.entry_id = entries.id
                    """
                )).mappings().fetchall()
            case 'other':
                recommended_entries = connection.execute(sqlalchemy.text(
                    """
                    SELECT *
                    FROM catalogs
                    JOIN users ON users.id = catalogs.user_id
                    JOIN entries ON entries.catalog_id = catalogs.id
                    JOIN other_entry on other_entry.entry_id = entries.id
                    """
                )).mappings().fetchall()

    return recommended_entries

@router.get("/{user_id}/social/search/{title}")
def search_catalogs():
    # searches (all ?) follower catalogs for a specified catalog title
    return "OK"
