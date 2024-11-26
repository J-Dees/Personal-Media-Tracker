from enum import Enum
from fastapi import APIRouter, Response, status
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/users/{user_id}/followees",
    tags=["following"],
)

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

@router.get("")
def get_following(user_id: int, 
                  name: str = "",
                  direction: asc_desc = asc_desc.asc,
                  page: int = 1):
    """Return a list of all users that you are following"""
    stats_statement = (
        sqlalchemy.select(
            sqlalchemy.func.count(db.social.c.following_id).label("total_rows"))
        .select_from(db.social)
        .join(db.users, db.users.c.id == db.social.c.following_id)
        .where(db.social.c.user_id == user_id)
        .where(db.users.c.name.ilike(f"%{name}%"))
    )
    #Statement for gathering the primary content returned.
    content_statement = (
        sqlalchemy.select(
            db.users.c.name)
        .select_from(db.social)
        .join(db.users, db.users.c.id == db.social.c.following_id)
        .where(db.social.c.user_id == user_id)
        .where(db.users.c.name.ilike(f"%{name}%"))
        .limit(db.MAX_PER_PAGE).offset(db.MAX_PER_PAGE*(page-1))
    )

    if (direction == "desc"):
        content_statement = content_statement.order_by(sqlalchemy.desc(db.users.c.name))
    else:
        content_statement = content_statement.order_by(db.users.c.name)

    return db.execute_search(stats_statement, content_statement, page)

@router.get("/catalogs")
def view_followees_catalogs(user_id:int , 
                            name: str = "",
                            catalog_name: str = "",
                            direction: asc_desc = asc_desc.asc,
                            page: int = 1):
    """View all public catalogs of a specific user that you are following """
    stats_statement = (
        sqlalchemy.select(
            sqlalchemy.func.count(db.social.c.following_id).label("total_rows"))
        .select_from(db.social)
        .join(db.users, db.users.c.id == db.social.c.following_id)
        .join(db.catalogs, db.catalogs.c.user_id == db.social.c.following_id)
        .where(db.social.c.user_id == user_id)
        .where(db.users.c.name.ilike(f"%{name}%"))
        .where(db.catalogs.c.name.ilike(f"%{catalog_name}%"))
        .where(db.catalogs.c.private == False)
    )
    #Statement for gathering the primary content returned.
    content_statement = (
        sqlalchemy.select(
            db.users.c.name.label("user"),
            db.catalogs.c.name.label("catalog_name"),
            db.catalogs.c.type)
        .select_from(db.social)
        .join(db.users, db.users.c.id == db.social.c.following_id)
        .join(db.catalogs, db.catalogs.c.user_id == db.social.c.following_id)
        .where(db.social.c.user_id == user_id)
        .where(db.users.c.name.ilike(f"%{name}%"))
        .where(db.catalogs.c.name.ilike(f"%{catalog_name}%"))
        .where(db.catalogs.c.private == False)
        .limit(db.MAX_PER_PAGE).offset(db.MAX_PER_PAGE*(page-1))
    )

    if (direction == "desc"):
        content_statement = content_statement.order_by(sqlalchemy.desc(db.catalogs.c.name))
    else:
        content_statement = content_statement.order_by(db.catalogs.c.name)

    return db.execute_search(stats_statement, content_statement, page)

@router.get("/entries")
def get_followees_entries(user_id: int, 
                    page: int = 1,
                    following_name: str="",
                    catalog: str="",
                    title: str = "",
                    recommend: bool = False,
                    order_by: entries_sort_col = entries_sort_col.title,
                    direction: asc_desc = asc_desc.asc,
                    return_type: entry_type = entry_type.movies):
    """Get all entries of a specific catalog from a user you are following"""

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

@router.get("/follow-recommendations")
def follow_recommendations(user_id: int):
    """Gets recommended users to follow."""
    with db.engine.begin() as connection:

        result = connection.execute(sqlalchemy.text(
            """
            -- SELECT all users the individual is following.
            WITH followings AS (
              SELECT
                social.following_id AS following
              FROM social
              WHERE social.user_id = :user_id
            ), 
            -- SELECT how many followings each user has in common with the individual.
            common_following AS (
              SELECT
                user_id AS user,
                count(following_id) AS total_common
              FROM social
              where following_id in (SELECT following FROM followings)
              GROUP BY user_id
              ORDER BY total_common DESC
            ), 
            -- SELECT all following from users that the individual isn't already following. Weight *  
            recommending AS (
              SELECT
                users.name AS recommendation
              FROM social
              JOIN common_following ON social.user_id = common_following.user
              JOIN users ON users.id = social.following_id
              WHERE 
               following_id NOT IN (SELECT following FROM followings) and
               following_id != :user_id
              GROUP BY following_id, users.name
              ORDER BY sum(total_common) DESC, users.name 
            )
            SELECT recommendation FROM recommending
            LIMIT 10
            """), {"user_id": user_id}).mappings().fetchall()
        
        #If no recommendations get the most popular as recomendations.
        if len(result) == 0:
            result = connection.execute(sqlalchemy.text(
                """
                SELECT
                  name
                from social
                Join users ON users.id = social.following_id
                Group by name
                ORDER BY count(following_id) desc
                LIMIT 5
                """)).mappings().fetchall()
            
            return {
                "About": "Please friend more people to come up with recommendations. Here is list of some popular people to follow.",
                "return": result
            }
        #Otherwise return the recommnedations.
        else: return result

@router.post("")
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

@router.delete("/{user_name}")
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
