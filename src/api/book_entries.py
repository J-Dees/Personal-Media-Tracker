from enum import Enum
from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from datetime import date


router = APIRouter(
    prefix="/entries/books",
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

def book_doesnt_exist(title: str, author: str) -> bool:
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT check_book_exists(:title, :author) as verified
            """
        ), {"title": title, "author": author}).first()
    return result.verified

class entries_order_by(str, Enum):
    book_title = "book_title"
    date_read = "date_read"
    rating = "rating"
class asc_desc(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/{user_id}/{catalog_name}")
def entry_search(user_id: int, 
                 catalog_name: str,
                 page: int = 1, 
                 opinion: str = "",
                 order_by: entries_order_by = entries_order_by.book_title,
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
        .where(db.catalogs.c.type == "books")
        .where(db.book_entry.c.opinion.ilike(f"%{opinion}%"))
    )
    #Statement for gathering the primary content returned.
    content_statement = (
        sqlalchemy.select(
            db.books.c.book_title,
            db.entries.c.private,
            db.entries.c.recommend,
            db.book_entry.c.rating,
            db.book_entry.c.date_read,
            db.book_entry.c.read_again,
            db.book_entry.c.opinion)
        .select_from(db.catalogs)
        .join(db.entries, db.entries.c.catalog_id == db.catalogs.c.id)
        .join(db.book_entry, db.book_entry.c.entry_id == db.entries.c.id)
        .join(db.books, db.book_entry.c.book_id == db.books.c.id)
        .where(db.catalogs.c.user_id == user_id)
        .where(db.catalogs.c.name == catalog_name)
        .where(db.catalogs.c.type == "books")
        .where(db.book_entry.c.opinion.ilike(f"%{opinion}%"))
        .limit(db.MAX_PER_PAGE).offset(db.MAX_PER_PAGE*(page-1))
    )

    #Append proper order_by to the query.
    if (direction == "desc"):
        content_statement = content_statement.order_by(sqlalchemy.desc(order_by))
    else:
        content_statement = content_statement.order_by(order_by)

    return db.execute_search(stats_statement, content_statement, page)

@router.post("/{user_id}/{catalog_name}")
def create_entry(user_id: int, catalog_name: str, entry: book_entries, response: Response):
    '''

    '''
    # insert into catalog table a new row with unqiue catalog id
    # do we want this to have a composite key for userid, catalog id, and entry id (ie user 1 catalog 1 entry 1, user 2 catalog 1 entry 1 etc)

    try:
        if (not catalog_belongs_to_user(user_id, catalog_name)):
            raise Exception("Catalog does not belong to user.")

        if (entry_exists(user_id, catalog_name, entry.title)):
            raise Exception("Entry already exists.")
        
        if (not book_doesnt_exist(entry.title, entry.author)):
            raise Exception("No Book matches that title and author.")
        
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
        response.status_code = status.HTTP_404_NOT_FOUND
        return str(e)

    return "OK"

class update_book_entries(BaseModel):
    opinion: str
    rating: float
    read_again: bool

@router.put("/{user_id}/{catalog_name}/{entry_title}")
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

@router.delete("/{user_id}/{catalog_name}/{entry_title}")
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