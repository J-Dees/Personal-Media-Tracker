from enum import Enum
from fastapi import APIRouter, Response, status
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/following",
    tags=["following"],
)

@router.get("/{user_id}")
def get_following(user_id: int, response: Response):
    """Return a list of all users that you are following"""
    with db.engine.begin() as connection:
        following = connection.execute(sqlalchemy.text(
            """
            SELECT name
            FROM users
            WHERE id IN (
                SELECT following_id
                FROM social
                JOIN users ON users.id = social.user_id
                WHERE social.user_id = :user_id
                ORDER BY users.name ASC
                )
            """
        ),
            {
                'user_id': user_id
            }
        ).mappings().fetchall()
    response.status_code = status.HTTP_200_OK
    return following



@router.get("/{user_id}/search_catalogs")
def view_following_catalogs(user_id:int , following_name: str, response: Response):
    """View all public catalogs of a specific user that you are following """
    try: 
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
        response.status_code = status.HTTP_200_OK
        return catalogs
    except:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "User by requested username not found in list of people you follow."

class entry_type(str, Enum):
    games = "games"
    books = "books"
    movies = "movies"
    other = "other"
class entries_sort_col(str, Enum):
    title = "title"
    rating_quality = "rating"
    date_timeplayed = "date"
class asc_desc(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/{user_id}/search_entries")
def get_recommended(user_id: int, 
                    page: int = 1,
                    following_name: str="",
                    catalog: str="",
                    title: str = "",
                    recommend: bool = False,
                    order_by: entries_sort_col = entries_sort_col.title,
                    direction: asc_desc = asc_desc.asc,
                    return_type: entry_type = entry_type.movies):
    """Get all recommended entries of a specific catalog from a user you are following"""

    #Start to build the stats and content statements generally for any entry type.
    stats_statement = (
        sqlalchemy.select(
            sqlalchemy.func.count(db.social.c.following_id).label("total_rows"))
        .select_from(db.social)
        .join(db.catalogs, db.catalogs.c.user_id == db.social.c.following_id)
        .join(db.entries, db.entries.c.catalog_id == db.catalogs.c.id)
        .join(db.users, db.users.c.id == db.social.c.following_id)
        .where(db.catalogs.c.private == False)
        .where(db.entries.c.private == False)
        .where(db.social.c.user_id == user_id)
        .where(db.users.c.name.ilike(f"%{following_name}%"))
        .where(db.catalogs.c.name.ilike(f"%{catalog}%"))
    )

    content_statement = (
        sqlalchemy.select(
            db.users.c.name,
            db.catalogs.c.name)
        .select_from(db.social)
        .join(db.catalogs, db.catalogs.c.user_id == db.social.c.following_id)
        .join(db.entries, db.entries.c.catalog_id == db.catalogs.c.id)
        .join(db.users, db.users.c.id == db.social.c.following_id)
        .where(db.catalogs.c.private == False)
        .where(db.entries.c.private == False)
        .where(db.social.c.user_id == user_id)
        .where(db.users.c.name.ilike(f"%{following_name}%"))
        .where(db.catalogs.c.name.ilike(f"%{catalog}%"))
        .limit(db.MAX_PER_PAGE).offset(db.MAX_PER_PAGE*(page-1))
    )
    #only limit results to recommended if recommend is true.
    if (recommend):
        content_statement = content_statement.where(db.entries.c.recommend == recommend)
        stats_statement = stats_statement.where(db.entries.c.recommend == recommend)

    #specialize the stats and content statements for a specific entry type.
    if (return_type == entry_type.movies):
        sort_col = {"title": "movie_title", "rating": "rating", "date": "date_seen"}
        #update stats to include only movies.
        stats_statement = (stats_statement
                           .join(db.movie_entry, db.movie_entry.c.entry_id == db.entries.c.id)
                           .join(db.movies, db.movies.c.id == db.movie_entry.c.movie_id)
                           .where(db.catalogs.c.type == "movies")
                           .where(db.movies.c.movie_title.ilike(f"%{title}%")))
        #update content to include only movies and return data about movies.
        content_statement = (content_statement.with_only_columns(
            db.users.c.name,
            db.catalogs.c.name.label("catalog"),
            db.movies.c.movie_title,
            db.movie_entry.c.rating,
            db.movie_entry.c.date_seen,
            db.movie_entry.c.watch_again,
            db.movie_entry.c.opinion)
            .join(db.movie_entry, db.movie_entry.c.entry_id == db.entries.c.id)
            .join(db.movies, db.movies.c.id == db.movie_entry.c.movie_id)
            .where(db.catalogs.c.type == "movies")
            .where(db.movies.c.movie_title.ilike(f"%{title}%"))
        )
        if (direction == "desc"):
            content_statement = content_statement.order_by(sqlalchemy.desc(sort_col.get(order_by)))
        else:
            content_statement = content_statement.order_by(sort_col.get(order_by))

    elif (return_type == entry_type.books):
        sort_col = {"title": "book_title", "rating": "rating", "date": "date_read"}
        #update stats to include only movies.
        stats_statement = (stats_statement
                           .join(db.book_entry, db.book_entry.c.entry_id == db.entries.c.id)
                           .join(db.books, db.books.c.id == db.book_entry.c.book_id)
                           .where(db.catalogs.c.type == "books")
                           .where(db.books.c.book_title.ilike(f"%{title}%")))
        #update content to include only movies and return data about movies.
        content_statement = (content_statement.with_only_columns(
            db.users.c.name,
            db.catalogs.c.name.label("catalog"),
            db.books.c.book_title,
            db.book_entry.c.rating,
            db.book_entry.c.date_read,
            db.book_entry.c.read_again,
            db.book_entry.c.opinion)
            .join(db.book_entry, db.book_entry.c.entry_id == db.entries.c.id)
            .join(db.books, db.books.c.id == db.book_entry.c.book_id)
            .where(db.catalogs.c.type == "books")
            .where(db.books.c.book_title.ilike(f"%{title}%"))
        )
        if (direction == "desc"):
            content_statement = content_statement.order_by(sqlalchemy.desc(sort_col.get(order_by)))
        else:
            content_statement = content_statement.order_by(sort_col.get(order_by))

    elif (return_type == entry_type.games):
        sort_col = {"title": "game_title", "rating": "rating", "date": "hours_played"}
        #update stats to include only movies.
        stats_statement = (stats_statement
                           .join(db.game_entry, db.game_entry.c.entry_id == db.entries.c.id)
                           .join(db.games, db.games.c.id == db.game_entry.c.game_id)
                           .where(db.catalogs.c.type == "games")
                           .where(db.games.c.game_title.ilike(f"%{title}%")))
        #update content to include only movies and return data about movies.
        content_statement = (content_statement.with_only_columns(
            db.users.c.name,
            db.catalogs.c.name.label("catalog"),
            db.games.c.game_title,
            db.game_entry.c.rating,
            db.game_entry.c.hours_played,
            db.game_entry.c.play_again,
            db.game_entry.c.opinion)
            .join(db.game_entry, db.game_entry.c.entry_id == db.entries.c.id)
            .join(db.games, db.games.c.id == db.game_entry.c.game_id)
            .where(db.catalogs.c.type == "games")
            .where(db.games.c.game_title.ilike(f"%{title}%"))
        )
        if (direction == "desc"):
            content_statement = content_statement.order_by(sqlalchemy.desc(sort_col.get(order_by)))
        else:
            content_statement = content_statement.order_by(sort_col.get(order_by))

    else:#return_type is other
        sort_col = {"title": "title", "rating": "quality", "date": "date_obtained"}
        #update stats to include only movies.
        stats_statement = (stats_statement
                           .join(db.other_entry, db.other_entry.c.entry_id == db.entries.c.id)
                           .where(db.catalogs.c.type == "other")
                           .where(db.other_entry.c.title.ilike(f"%{title}%")))
        #update content to include only movies and return data about movies.
        content_statement = (content_statement.with_only_columns(
            db.users.c.name,
            db.catalogs.c.name.label("catalog"),
            db.other_entry.c.title,
            db.other_entry.c.quality,
            db.other_entry.c.price,
            db.other_entry.c.date_obtained,
            db.other_entry.c.description)
            .join(db.other_entry, db.other_entry.c.entry_id == db.entries.c.id)
            .where(db.catalogs.c.type == "other")
            .where(db.other_entry.c.title.ilike(f"%{title}%"))
        )
        if (direction == "desc"):
            content_statement = content_statement.order_by(sqlalchemy.desc(sort_col.get(order_by)))
        else:
            content_statement = content_statement.order_by(sort_col.get(order_by))
    
    return db.execute_search(stats_statement, content_statement, page)
    # """ view all catalog entries that are flagged as recommended in a given catalog of a user that you are following"""
    # # this is probably something we can implement into a user's own catalogs as well

    # with db.engine.begin() as connection:
    #     result = connection.execute(sqlalchemy.text(
    #         """
    #         SELECT user_id, following_id
    #         FROM social
    #         JOIN users ON users.id = social.following_id
    #         WHERE users.name = :following_name
    #         AND user_id = :user_id
    #         """
    #     ), 
    #         {
    #             'following_name': following_name,
    #             'user_id': user_id
    #         }
    #     ).first()

    # if result == None:
    #     print(f"User is not following {following_name}")
    #     return []

    # with db.engine.begin() as connection:
    #     catalog_type = connection.execute(sqlalchemy.text(
    #         """
    #         SELECT type
    #         FROM catalogs
    #         JOIN users ON users.id = catalogs.user_id
    #         WHERE users.name = :following_name
    #         """
    #     ),{'following_name': following_name}).scalar()


    # with db.engine.begin() as connection:
    #     match catalog_type:
    #         case 'games':
    #             recommended_entries = connection.execute(sqlalchemy.text(
    #                 """
    #                 SELECT
    #                     games.game_title,
    #                     games.year,
    #                     game_entry.entry_id,
    #                     game_entry.hours_played,
    #                     game_entry.opinion,
    #                     game_entry.rating,
    #                     game_entry.recommend
    #                 FROM catalogs
    #                 JOIN users ON users.id = catalogs.user_id
    #                 JOIN entries ON entries.catalog_id = catalogs.id
    #                 JOIN game_entry ON game_entry.entry_id = entries.id
    #                 JOIN games ON games.id = game_entry.game_id
    #                 """
    #             )).mappings().fetchall()
    #         case 'movies':
    #             recommended_entries = connection.execute(sqlalchemy.text(
    #                 """
    #                 SELECT 
    #                     movies.movie_title,
    #                     movies.year,
    #                     movie_entry.date_seen, 
    #                     movie_entry.opinion, 
    #                     movie_entry.rating, 
    #                     movie_entry.watch_again,
    #                     entries.recommend
    #                 FROM catalogs
    #                 JOIN users ON users.id = catalogs.user_id
    #                 JOIN entries ON entries.catalog_id = catalogs.id
    #                 JOIN movie_entry ON movie_entry.entry_id = entries.id
    #                 JOIN movies ON movies.id = movie_entry.movie_id
    #                 """
    #             )).mappings().fetchall()
    #         case 'books':
    #             recommended_entries = connection.execute(sqlalchemy.text(
    #                 """
    #                 SELECT
    #                     books.book_title,
    #                     books.author,
    #                     book_entry.date_read,
    #                     book_entry.opinion,
    #                     book_entry.rating,
    #                     book_entry.read_again
    #                     entries.recommend
    #                 FROM catalogs
    #                 JOIN users ON users.id = catalogs.user_id
    #                 JOIN entries ON entries.catalog_id = catalogs.id
    #                 JOIN book_entry ON book_entry.entry_id = entries.id
    #                 JOIN books ON books.id = book_entry.book_id
    #                 """
    #             )).mappings().fetchall()
    #         case 'other':
    #             recommended_entries = connection.execute(sqlalchemy.text(
    #                 """
    #                 SELECT
    #                     other_entry.title,
    #                     other_entry.description,
    #                     other_entry.price,
    #                     other_entry.quality,
    #                     entries.recommend
    #                 FROM catalogs
    #                 JOIN users ON users.id = catalogs.user_id
    #                 JOIN entries ON entries.catalog_id = catalogs.id
    #                 JOIN other_entry ON other_entry.entry_id = entries.id
    #                 """
    #             )).mappings().fetchall()

    # return recommended_entries

# @router.get("/{user_id}/social/search/{title}")
# def search_catalogs():
#     # searches (all ?) follower catalogs for a specified catalog title
#     return "OK"

@router.post("/{user_id}")
def follow_user(user_id: int, user_name: str, response: Response):
    """Follow a user by their username"""
    following_id = None
    # outer: try to follow user, if username is not recognized in users table throw 404 response
    try:
        with db.engine.begin() as connection:
            # inner: try to see if user to follow is already in following list or is yourself
            # under exception condition, proceed as normal because the user is not yourself or already somebody you follow
            try:
                result = connection.execute(sqlalchemy.text(
                    """
                    SELECT following_id
                    FROM social
                    WHERE following_id = (
                        SELECT id
                        FROM users
                        WHERE name = :user_name
                        ) AND user_id = :user_id
                    """), {'user_id': user_id, 'user_name': user_name}).scalar_one()
                response.status_code = status.HTTP_400_BAD_REQUEST
                return "User already in list of people you follow."
            except:
                new_follow = connection.execute(sqlalchemy.text(
                    """
                    SELECT id
                    FROM users
                    WHERE name = :user_name
                    """), {'user_name': user_name}).scalar_one()
                if new_follow == user_id:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return "Unable to add yourself to list of people to follow."
                else:
                    connection.execute(sqlalchemy.text(
                        """
                        INSERT INTO social (user_id, following_id)
                        VALUES(:user_id, :new_follow)
                        """
                    ),
                        {
                            'user_id': user_id,
                            'new_follow': new_follow
                        }
                    )
                    response.status_code = status.HTTP_200_OK
                    return "OK"
    except:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "User with requested username does not exist."

@router.delete("/{user_id}")
def unfollow_user(user_id: int, user_name: str, response: Response):
    """Remove user from list of people to follow by username"""
    try:
        with db.engine.begin() as connection:
                # check if user in follow list
                check = connection.execute(sqlalchemy.text(
                    """
                    SELECT following_id
                    FROM social
                    WHERE user_id = :user AND following_id = (
                        SELECT id
                        FROM users
                        WHERE name = :user_name
                        );
                    """),
                    {
                        'user_name': user_name,
                        'user': user_id,
                    }
                ).one()
                connection.execute(sqlalchemy.text(
                    """
                    DELETE FROM social
                    WHERE user_id = :user AND following_id = (
                        SELECT id
                        FROM users
                        WHERE name = :user_name
                        )
                    """
                ),
                    {
                        'user_name': user_name,
                        'user': user_id,
                    }
                )
        response.status_code = status.HTTP_204_NO_CONTENT
        return "User successfully removed from people you follow."
    except:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "User by the requested name not found in list of people you follow."




# @router.get("/{user_id}/social/search")
# def get_followers(user_id: int):
#     """ gets user_id's followers """
#     with db.engine.begin() as connection:
#         followers = connection.execute(sqlalchemy.text(
#             """
#             SELECT users.name
#             FROM social
#             JOIN users ON users.id = social.user_id
#             WHERE social.following_id = :user_id
#             ORDER BY users.name ASC
#             """
#         ),
#             {
#                 'user_id': user_id
#             }
#         ).mappings().fetchall()

#     return followers

# @router.post("/{user_id}/social")
# def follower_user(user_id: int, user_name: str):
#     """ user_id will follow a user with user_name """
#     with db.engine.begin() as connection:
#         connection.execute(sqlalchemy.text(
#             """
#             INSERT INTO social (user_id, following_id)
#             VALUES(
#                 :user_id,
#                 (
#                     SELECT id
#                     FROM users
#                     WHERE users.name = :user_name
#                 )
#             )
#             """
#         ),
#             {
#                 'user_id': user_id,
#                 'user_name': user_name
#             }
#         )
#     return "OK"

# @router.delete("/{user_id}/social/{following_id}")
# def unfollow(user_id: int, following_name: str):
#     """ user_id unfollows following_name """
#     with db.engine.begin() as connection:
#         try:
#             result = connection.execute(sqlalchemy.text(
#                 """
#                 DELETE FROM social
#                 WHERE following_id = (
#                     SELECT following_id
#                     FROM users
#                     WHERE users.name = :following_name
#                     )
#                     and social.user_id = :user_id;

#                 SELECT user_id, following_id
#                 FROM social
#                 WHERE user_id = :user_id
#                 AND following_id = (
#                     SELECT following_id
#                     FROM users
#                     WHERE users.name = :following_name
#                 )
#                 """
#             ),
#                 {
#                     'following_name': following_name,
#                     'user_id': user_id,
#                     'following_name': following_name,
#                     'user_id': user_id
#                 }
#             ).first()
#         except ():
#             return False

#     if result != None:
#         print("row not deleted")
#         return False
#     else:
#         return True