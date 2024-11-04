from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from datetime import date


router = APIRouter(
    prefix="/user",
    tags=["movies_entries"],
)

class movie_entries(BaseModel):
    title: str
    year: int
    opinion: str
    rating: float
    date_seen: date
    watch_again: bool
    recommend: bool
    private: bool

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

def movie_doesnt_exist(title: str, year: int) -> bool:
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT check_movie_exists(:title, :year) as verified
            """
        ), {"title": title, "year": year}).first()
    return result.verified

@router.post("/{user_id}/catalogs/{catalog_name}/movie_entries")
def create_movie_entry(user_id: int, catalog_name: str, entry: movie_entries, response: Response):
    '''

    '''
    # insert into catalog table a new row with unqiue catalog id
    # do we want this to have a composite key for userid, catalog id, and entry id (ie user 1 catalog 1 entry 1, user 2 catalog 1 entry 1 etc)

    try:
        if (not catalog_belongs_to_user(user_id, catalog_name)):
            raise Exception("Catalog does not belong to user.")

        if (entry_exists(user_id, catalog_name, entry.title)):
            raise Exception("Entry already exists.")
        
        if (movie_doesnt_exist(entry.title, entry.year)):
            raise Exception("No movie matches that title and year.")

        with db.engine.begin() as connection:
            entry_id = connection.execute(sqlalchemy.text(
                """
                INSERT INTO
                    entries (catalog_id, private, recommend)
                    (SELECT catalogs.id, :private, :recommend FROM catalogs WHERE name = :catalog_name AND user_id = :user_id)
                RETURNING id
                """
            ), {"private": entry.private, "recommend": entry.recommend, "catalog_name": catalog_name, "user_id": user_id}).one()

            connection.execute(sqlalchemy.text(
                """
                INSERT INTO
                    movie_entry (entry_id, movie_id, date_seen, opinion, rating, watch_again)
                    (
                        SELECT :entry_id, movies.id, :date_seen, :opinion, :rating, :watch_again
                        FROM movies
                        WHERE movie_title = :movie_title
                        AND year = :year
                    )
                """
            ), {
                "entry_id": entry_id.id,
                "date_seen": entry.date_seen,
                "opinion": entry.opinion,
                "rating": entry.rating,
                "watch_again": entry.watch_again,
                "movie_title": entry.title,
                "year": entry.year
            })
    
    except Exception as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return str(e)

    return "OK"

        
@router.get("/{user_id}/catalogs/{catalog_name}/movie_entries/search")
def entry_search():
    # find a specific entry in the current catalog with the given query
    return "OK"

class update_movie_entries(BaseModel):
    opinion: str
    rating: float
    date_seen: date
    watch_again: bool


@router.put("/{user_id}/catalogs/{catalog_name}/movie_entries/{entry_title}")
def update_entry(user_id: int, catalog_name: str, entry_title: str, entry: update_movie_entries):
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
                    movie_entry
                SET
                    date_seen = :date_seen,
                    opinion = :opinion,
                    rating = :rating,
                    watch_again = :watch_again
                WHERE entry_id =
                    (
                    SELECT entry_id
                    FROM entries
                    JOIN movie_entry ON movie_entry.entry_id = entries.id
                    JOIN movies ON movies.id = movie_entry.movie_id
                    WHERE movie_title = :entry_title
                    )
                """
            ), parameters)
    
    except Exception as e:
        print("Error:", e)

    return "OK"

@router.delete("/{user_id}/catalogs/{catalog_name}/movie_entries/{entry_title}")
def delete_entry(user_id: int, catalog_name: str, entry_title: str):
    # DELETE FROM entries specified title

    try:
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
                    JOIN movie_entry ON movie_entry.entry_id = entries.id
                    JOIN movies on movies.id = movie_entry.movie_id
                    WHERE movie_title = :entry_title
                    )
                """
            ), {"entry_title": entry_title})
    except Exception as e:
        print("Error:", e)

    return "OK"