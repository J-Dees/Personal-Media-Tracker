from fastapi import APIRouter
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from datetime import date


router = APIRouter(
    prefix="/user",
    tags=["book_entries"],
)

class book_entries(BaseModel):
    title: str
    author: str
    opinion: str
    rating: float
    date_read: date
    read_again: bool
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

@router.post("/{user_id}/catalogs/{catalog_name}/book_entries")
def create_entry(user_id: int, catalog_name: str, entry: book_entries):
    '''

    '''
    # insert into catalog table a new row with unqiue catalog id
    # do we want this to have a composite key for userid, catalog id, and entry id (ie user 1 catalog 1 entry 1, user 2 catalog 1 entry 1 etc)

    try:
        if (not catalog_belongs_to_user(user_id, catalog_name)):
            raise Exception("Catalog does not belong to user.")

        if (entry_exists(user_id, catalog_name, entry.title)):
            raise Exception("Entry already exists.")

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
                    book_entry (entry_id, book_id, date_read, opinion, rating, read_again)
                    (
                        SELECT :entry_id, books.id, :date_read, :opinion, :rating, :read_again
                        FROM books
                        WHERE book_title = :book_title
                        AND author = :author
                    )
                """
            ), {
                "entry_id": entry_id.id,
                "date_read": entry.date_read,
                "opinion": entry.opinion,
                "rating": entry.rating,
                "read_again": entry.read_again,
                "book_title": entry.title,
                "author": entry.author
            })
    
    except Exception as e:
        print("Error:",e)

    return "OK"

        
@router.get("/{user_id}/catalogs/{catalog_name}/book_entries/search")
def entry_search():
    # find a specific entry in the current catalog with the given query
    return "OK"

class update_book_entries(BaseModel):
    opinion: str
    rating: float
    read_again: bool

@router.put("/{user_id}/catalogs/{catalog_name}/book_entries/{entry_title}")
def update_entry(user_id: int, catalog_name: str, entry_title: str, entry: update_book_entries):
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
                    book_entry
                SET
                    opinion = :opinion,
                    rating = :rating,
                    read_again = :read_again
                WHERE entry_id =
                    (
                        SELECT entry_id
                        FROM entries
                        JOIN book_entry ON book_entry.entry_id = entries.id
                        JOIN books on books.id = book_entry.book_id
                        WHERE book_title = :entry_title
                    )
                """
            ), parameters)
    
    except Exception as e:
        print("Error:", e)

    return "OK"

@router.delete("/{user_id}/catalogs/{catalog_name}/book_entries/{entry_title}")
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
                        JOIN book_entry ON book_entry.entry_id = entries.id
                        JOIN books on books.id = book_entry.book_id
                        WHERE book_title = :entry_title
                    )
                """
            ), {"entry_title": entry_title})

    except Exception as e:
        print("Error:", e)
    return "OK"