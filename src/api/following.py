from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/user",
    tags=["following"],
)

@router.get("/{user_id}/social/{follower_name}/catalogs")
def view_following_catalogs(user_id:int , following_name: str):
    """ view catalogs of a user that you are following """

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT user_id, following_id
            FROM social
            JOIN users ON users.id = social.following_id
            WHERE users.name = :following_name
            AND user_id = :user_id
            """
        ), 
            {
                'following_name': following_name,
                'user_id': user_id
            }
        ).first()

    if result == None:
        print(f"User is not following {following_name}")
        return []

    with db.engine.begin() as connection:
        catalogs = connection.execute(sqlalchemy.text(
            """
            SELECT catalogs.name, catalogs.type
            FROM catalogs
            JOIN users ON users.id = catalogs.user_id
            WHERE users.name = :following_name
            AND catalogs.private = FALSE
            """
        ), 
            {
                'following_name': following_name
            }
        ).mappings().fetchall()

    return catalogs

@router.get("/{user_id}/social/{following_name}/catalogs/{catalog}/recommendations")
def get_recommended(user_id: int, following_name: str, catalog: str):
    """ view all catalog entries that are flagged as recommended in a given catalog of a user that you are following"""
    # this is probably something we can implement into a user's own catalogs as well

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT user_id, following_id
            FROM social
            JOIN users ON users.id = social.following_id
            WHERE users.name = :following_name
            AND user_id = :user_id
            """
        ), 
            {
                'following_name': following_name,
                'user_id': user_id
            }
        ).first()

    if result == None:
        print(f"User is not following {following_name}")
        return []

    with db.engine.begin() as connection:
        catalog_type = connection.execute(sqlalchemy.text(
            """
            SELECT type
            FROM catalogs
            JOIN users ON users.id = catalogs.user_id
            WHERE users.name = :following_name
            """
        ),{'following_name': following_name}).scalar()


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
                    JOIN movie_entry on movie_entry.entry_id = entries.id
                    """
                )).mappings().fetchall()
            case 'books':
                recommended_entries = connection.execute(sqlalchemy.text(
                    """
                    SELECT *
                    FROM catalogs
                    JOIN users ON users.id = catalogs.user_id
                    JOIN entries ON entries.catalog_id = catalogs.id
                    JOIN book_entry on book_entry.entry_id = entries.id
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

@router.get("/{user_id}/social/search")
def get_followers(user_id: int):
    """ gets user_id's followers """
    with db.engine.begin() as connection:
        followers = connection.execute(sqlalchemy.text(
            """
            SELECT users.name
            FROM social
            JOIN users ON users.id = social.user_id
            WHERE social.following_id = :user_id
            ORDER BY users.name ASC
            """
        ),
            {
                'user_id': user_id
            }
        ).mappings().fetchall()

    return followers

@router.post("/{user_id}/social")
def follower_user(user_id: int, user_name: str):
    """ user_id will follow a user with user_name """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO social (user_id, following_id)
            VALUES(
                :user_id,
                (
                    SELECT id
                    FROM users
                    WHERE users.name = :user_name
                )
            )
            """
        ),
            {
                'user_id': user_id,
                'user_name': user_name
            }
        )
    return "OK"

@router.delete("/{user_id}/social/{following_id}")
def unfollow(user_id: int, following_name: str):
    """ user_id unfollows following_name """
    with db.engine.begin() as connection:
        try:
            result = connection.execute(sqlalchemy.text(
                """
                DELETE FROM social
                WHERE following_id = (
                    SELECT following_id
                    FROM users
                    WHERE users.name = :following_name
                    )
                    and social.user_id = :user_id;

                SELECT user_id, following_id
                FROM social
                WHERE user_id = :user_id
                AND following_id = (
                    SELECT following_id
                    FROM users
                    WHERE users.name = :following_name
                )
                """
            ),
                {
                    'following_name': following_name,
                    'user_id': user_id,
                    'following_name': following_name,
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