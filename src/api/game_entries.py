from enum import Enum
from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/users/{user_id}/catalogs/{catalog_name}/game-entries",
    tags=["game_entries"],
)

class game_entries(BaseModel):
    title: str
    year: int
    opinion: str
    rating: float
    hours_played: float
    play_again: bool
    recommend: bool
    private: bool


class entries_order_by(str, Enum):
    game_title = "game_title"
    hours_played = "hours_played"
    rating = "rating"
    date_created = "date_created"
class asc_desc(str, Enum):
    asc = "asc"
    desc = "desc"
        
@router.get("")
def entry_search(user_id: int, 
                 catalog_name: str,
                 response: Response,
                 page: int = 1, 
                 opinion: str = "",
                 order_by: entries_order_by = entries_order_by.game_title,
                 direction: asc_desc = asc_desc.asc):
    """Search one of your catalog's game_entries. Note that the catalog must be of the game type.
        - catalog_name: A String that must match an exact catalog_name of yours.
        - page: The page of results to return.
        - opinion: A String that each entry returned must contain.
        - order_by: Specifies a value to sort the results by. 
        - direction: The sort order of the results in either `asc` or `desc` order."""
    # find a specific entry in the current catalog with the given query
    stats_statement = (
        sqlalchemy.select(
            sqlalchemy.func.count(db.entries.c.id).label("total_rows"))
        .select_from(db.entries)
        .join(db.catalogs, db.entries.c.catalog_id == db.catalogs.c.id)
        .join(db.game_entry, db.entries.c.id == db.game_entry.c.entry_id)
        .where(db.catalogs.c.user_id == user_id)
        .where(db.catalogs.c.name == catalog_name)
        .where(db.catalogs.c.type == "games")
        .where(db.game_entry.c.opinion.ilike(f"%{opinion}%"))
    )
    #Statement for gathering the primary content returned.
    content_statement = (
        sqlalchemy.select(
            db.games.c.game_title,
            db.entries.c.private,
            db.entries.c.recommend,
            db.game_entry.c.rating,
            db.game_entry.c.hours_played,
            db.game_entry.c.play_again,
            db.game_entry.c.opinion)
        .select_from(db.catalogs)
        .join(db.entries, db.entries.c.catalog_id == db.catalogs.c.id)
        .join(db.game_entry, db.game_entry.c.entry_id == db.entries.c.id)
        .join(db.games, db.game_entry.c.game_id == db.games.c.id)
        .where(db.catalogs.c.user_id == user_id)
        .where(db.catalogs.c.name == catalog_name)
        .where(db.catalogs.c.type == "games")
        .where(db.game_entry.c.opinion.ilike(f"%{opinion}%"))
        .limit(db.MAX_PER_PAGE).offset(db.MAX_PER_PAGE*(page-1))
    )

    #Append proper order_by to the query.
    if (direction == "desc"):
        content_statement = content_statement.order_by(sqlalchemy.desc(order_by))
    else:
        content_statement = content_statement.order_by(order_by)

    #Break ties by the order of entries_order_by.
    for item in entries_order_by:
        if item.value != order_by:
            content_statement = content_statement.order_by(item)

    return db.execute_search(stats_statement, content_statement, page, response)

@router.post("")
def create_game_entry(user_id: int, catalog_name: str, entry: game_entries, response: Response):
    '''
    Cretes a new game_entry in the catalog catalg_name.\\ 
    The entry must not already exist and the catalog must be of the Type 'games'
        - title: Must exactly match a title found in the games database.
        - year: Must exactly match the year attached to the title find in the games database.
        - opinion: A string stating your opinions on the game.
        - rating: A rating of 0-10 inclusive.
        - hours_played: An approximate amount of hours playing a game.
        - play_again: A boolean ('true' or 'false') on whether you would play the game again.
        - recommend: A boolean ('true' or 'false') on whether you would recommend the game to another.
        - private: A boolean ('true' or 'false') on if you want others to see this entry.
    '''

    try:
        with db.engine.begin() as connection:
            # Checks if:
            # 1. catalog belongs to user
            # 2. entry is already in catalog
            # 3. entry is in database
            # Raises exception if there are any conflicts
            valid_request = connection.execute(sqlalchemy.text(
                """
                select 
                    check_catalog_user_relationship(:user_id, :catalog_name, 'games') as catalog_user_relationship,
                    check_entry_in_catalog(:user_id, :catalog_name, 'games', :entry_name) as entry_in_catalog,
                    check_game_entry_exists(:entry_name, :entry_year) as entry_exists,
                    check_rating_bounds(:rating) AS within_rating_bounds
                """
            ), {"user_id": user_id, "catalog_name": catalog_name, "entry_name": entry.title, "entry_year": entry.year, "rating": entry.rating}).first()

            if (not valid_request.catalog_user_relationship):
                raise Exception("Catalog does not belong to user.")
            
            if (valid_request.entry_in_catalog):
                raise Exception("Entry already exists in catalog.")
            
            if (not valid_request.entry_exists):
                raise Exception("No game matches that title and year")
            
            if (not valid_request.within_rating_bounds):
                raise Exception("Outside of valid rating range of [0-10].")


            entry_id = connection.execute(sqlalchemy.text(
                """
                INSERT INTO
                    entries (catalog_id, private, recommend)
                    (SELECT catalogs.id, :private, :recommend FROM catalogs 
                        WHERE name = :catalog_name 
                        AND user_id = :user_id
                        AND type = 'games')
                RETURNING id

                """
            ), {"catalog_name": catalog_name, "private": entry.private, "recommend": entry.recommend, "user_id": user_id}).one()

            connection.execute(sqlalchemy.text(
                """
                INSERT INTO 
                    game_entry (entry_id, game_id, hours_played, opinion, rating, play_again)
                    (
                        SELECT :entry_id, games.id, :hours_played, :opinion, :rating, :play_again
                        FROM games
                        WHERE game_title = :game_title
                        AND year = :year
                    )
                """
            ), {
                "entry_id": entry_id.id,
                "hours_played": entry.hours_played,
                "opinion": entry.opinion,
                "rating": entry.rating,
                "play_again": entry.play_again,
                "game_title": entry.title,
                "year": entry.year
            })

    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": f"{e}"}

    response.status_code = status.HTTP_201_CREATED
    return {"response": "Game entry created."}

class update_game_entries(BaseModel):
    opinion: str
    rating: float
    hours_played: float
    play_again: bool
    
@router.put("/{entry_title}")
def update_entry(user_id: int, catalog_name: str, entry_title: str, entry: update_game_entries, response: Response):
    """Given a existing tuple of user_id, catalog_name, and entry_title you can update the values of that entry."""
    # update any value of the specified entry

    try:
        with db.engine.begin() as connection:
            # Checks if:
            # 1. Catalog belongs to user
            # 2. Entry is in catalog
            # Raises exception if there are any conflicts
            valid_request = connection.execute(sqlalchemy.text(
                """
                select 
                    check_catalog_user_relationship(:user_id, :catalog_name, 'games') as catalog_user_relationship,
                    check_entry_in_catalog(:user_id, :catalog_name, 'games', :entry_name) as entry_in_catalog
                """
            ), {"user_id": user_id, "catalog_name": catalog_name, "entry_name": entry_title}).first()

            if (not valid_request.catalog_user_relationship) :
                raise Exception("Catalog does not belong to user.")
            
            if (not valid_request.entry_in_catalog):
                raise Exception("Entry already exists in catalog.")
            

            # Get catalog id
            catalog_id = connection.execute(sqlalchemy.text(
                """
                SELECT
                    id
                FROM
                    catalogs
                WHERE
                    user_id = :user_id and
                    name = :catalog_name and
                    type = 'games'
                """
            ), {"user_id": user_id, "catalog_name": catalog_name}).one()

            parameters = entry.dict()
            parameters.update({"entry_title": entry_title})
            parameters.update({"catalog_id": catalog_id.id})
            connection.execute(sqlalchemy.text(
                """
                UPDATE
                    game_entry
                SET
                    hours_played = :hours_played,
                    rating = :rating,
                    opinion = :opinion,
                    play_again = :play_again
                WHERE entry_id = 
                    (
                    SELECT entry_id
                    FROM entries
                    JOIN game_entry ON game_entry.entry_id = entries.id
                    JOIN games on games.id = game_entry.game_id
                    WHERE game_title = :entry_title and entries.catalog_id = :catalog_id
                    )
                """
            ), parameters)
        response.status_code = status.HTTP_202_ACCEPTED
        return {"response": f"Entry '{entry_title}' updated successfully"}

    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"{e}"}

@router.delete("/{entry_title}")
def delete_entry(user_id: int, catalog_name: str, entry_title: str, response: Response):
    """Given a existing tuple of user_id, catalog_name, and entry_title you can delete the entry."""
    # DELETE FROM entries specified title

    try:
        with db.engine.begin() as connection:
            # Checks if:
            # 1. Catalog belongs to user
            # 2. Entry is in catalog
            # Raises exception if there are any conflicts
            valid_request = connection.execute(sqlalchemy.text(
                """
                select 
                    check_catalog_user_relationship(:user_id, :catalog_name, 'games') as catalog_user_relationship,
                    check_entry_in_catalog(:user_id, :catalog_name, 'games', :entry_name) as entry_in_catalog
                """
            ), {"user_id": user_id, "catalog_name": catalog_name, "entry_name": entry_title}).first()

            if (not valid_request.catalog_user_relationship) :
                raise Exception("Catalog does not belong to user.")
            
            if (not valid_request.entry_in_catalog):
                raise Exception("Entry already exists in catalog.")


            # Get catalog id
            catalog_id = connection.execute(sqlalchemy.text(
                """
                SELECT
                    id
                FROM
                    catalogs
                WHERE
                    user_id = :user_id and
                    name = :catalog_name and
                    type = 'games'
                """
            ), {"user_id": user_id, "catalog_name": catalog_name}).one()

            connection.execute(sqlalchemy.text(
                """
                DELETE FROM
                    entries
                WHERE id = 
                    (
                    SELECT entry_id
                    FROM entries
                    JOIN game_entry ON game_entry.entry_id = entries.id
                    JOIN games on games.id = game_entry.game_id
                    WHERE game_title = :entry_title and catalog_id = :catalog_id
                    )
                """
            ), {"entry_title": entry_title, "catalog_id": catalog_id.id})
        response.status_code = status.HTTP_204_NO_CONTENT
        return {"response": f"Entry '{entry_title}' deleted successfully"}

    except Exception as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"{e}"}