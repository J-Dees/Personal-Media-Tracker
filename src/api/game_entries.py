from enum import Enum
from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/user",
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
        
@router.get("/{user_id}/catalogs/{catalog_name}/entries/search")
def entry_search(user_id: int, 
                 catalog_name: str,
                 page: int = 1, 
                 opinion: str = "",
                 order_by: entries_order_by = entries_order_by.game_title,
                 direction: asc_desc = asc_desc.asc):
    """Search a specific catalog's game_entries"""
    # find a specific entry in the current catalog with the given query
    stats_statement = (
        sqlalchemy.select(
            sqlalchemy.func.count(db.entries.c.id).label("total_rows"))
        .select_from(db.entries)
        .join(db.catalogs, db.entries.c.catalog_id == db.catalogs.c.id)
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

    return db.execute_search(stats_statement, content_statement, page)

def catalog_belongs_to_user(user_id: int, catalog_name: str) -> bool:
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT
                verify_catalog_belongs_user(:catalog_name, :user_id) as verified
            """
        ), {"catalog_name": catalog_name, "user_id": user_id}).first()

    return result.verified

def entry_exists(user_id: int, catalog_name: str, entry_title: str) -> bool:
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT check_entry_exists(:catalog_name, :user_id, :entry_title) as verified
            """
        ), {"catalog_name": catalog_name, "user_id": user_id, "entry_title": entry_title}).first()
    return result.verified

def game_doesnt_exist(title: str, year: int) -> bool:
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT check_game_exists(:title, :year) as verified
            """
        ), {"title": title, "year": year}).first()
    return result.verified

@router.post("/{user_id}/catalogs/{catalog_name}/game_entries")
def create_game_entry(user_id: int, catalog_name: str, entry: game_entries, response: Response):
    '''
    Creates a new entry for the user in a catalog.
    Does not accept duplicate entry titles
    '''
    # insert into catalog table a new row with unqiue catalog id
    # do we want this to have a composite key for userid, catalog id, and entry id (ie user 1 catalog 1 entry 1, user 2 catalog 1 entry 1 etc)

    try:
        # Verify catalog belongs to user
        if (not catalog_belongs_to_user(user_id, catalog_name)):
            raise Exception("Catalog does not belong to user.")
        
        # Check if entry already exists
        if (entry_exists(user_id, catalog_name, entry.title)):
            raise Exception("Entry already exists.")
        
        if (not game_doesnt_exist(entry.title, entry.year)):
            raise Exception("No game matches that title and year.")

        with db.engine.begin() as connection:
            entry_id = connection.execute(sqlalchemy.text(
                """
                INSERT INTO
                    entries (catalog_id, private, recommend)
                    (SELECT catalogs.id, :private, :recommend FROM catalogs WHERE name = :catalog_name AND user_id = :user_id)
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
        response.status_code = status.HTTP_404_NOT_FOUND
        return str(e)

    return "OK"

class update_game_entries(BaseModel):
    opinion: str
    rating: float
    hours_played: float
    play_again: bool
    
@router.put("/{user_id}/catalogs/{catalog_name}/entries/{entry_title}")
def update_entry(user_id: int, catalog_name: str, entry_title: str, entry: update_game_entries):
    # update any value of the specified entry

    try:
        if (not catalog_belongs_to_user(user_id, catalog_name)):
            raise Exception("Catalog does not belong to user.")
        
        if (not entry_exists(user_id, catalog_name, entry_title)):
            raise Exception("Entry does not exist.")


        with db.engine.begin() as connection:
            parameters = entry.dict()
            parameters.update({"entry_title": entry_title})

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
                    WHERE game_title = :entry_title
                    )
                """
            ), parameters)
        
    except Exception as e:
        print("Error:", e)

    return "OK"

@router.delete("/{user_id}/catalogs/{catalog_name}/game_entries/{entry_title}")
def delete_entry(user_id: int, catalog_name: str, entry_title: str):
    # DELETE FROM entries specified title

    try:
        # Verify catalog belongs to user
        if (not catalog_belongs_to_user(user_id, catalog_name)):
            raise Exception("Catalog does not belong to user.")
        if (not entry_exists(user_id, catalog_name, entry_title)):
            raise Exception("Entry does not exist.")
        
        with db.engine.begin() as connection:
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
                    WHERE game_title = :entry_title
                    )
                """
            ), {"entry_title": entry_title})
    except Exception as e:
        print("Error:", e)

    return "OK"