from enum import Enum
from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from datetime import date


router = APIRouter(
    prefix="/users/{user_id}/catalogs/{catalog_name}/book-entries",
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

@router.get("")
def entry_search(user_id: int, 
                 catalog_name: str,
                 page: int = 1, 
                 opinion: str = "",
                 order_by: entries_order_by = entries_order_by.book_title,
                 direction: asc_desc = asc_desc.asc):
    """Search one of your catalog's book_entries. Note that the catalog must be of the book type.
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

@router.post("")
def create_entry(user_id: int, catalog_name: str, entry: book_entries, response: Response):
    '''
    Cretes a new book_entry in the catalog catalg_name.\\ 
    The entry must not already exist and the catalog must be of the Type ''books
        - title: Must exactly match a title found in the books database.
        - author: Must exactly match the author attached to the title found in the books database.
        - opinion: A string stating your opinions of the book.
        - rating: A rating of 0-10 inclusive.
        - date_read: Date on when you read the book. Must be of the form "YYYY-MM-DD".
        - read_again: A boolean ('true' or 'false') on whether you would read the book again.
        - recommend: A boolean ('true' or 'false') on whether you would recommend the book to another person.
        - private: A boolean ('true' or 'false') on if you want others to see this entry.
    '''
    # insert into catalog table a new row with unqiue catalog id
    # do we want this to have a composite key for userid, catalog id, and entry id (ie user 1 catalog 1 entry 1, user 2 catalog 1 entry 1 etc)

    try:
        if (not catalog_belongs_to_user(user_id, catalog_name)):
            response.status_code = status.HTTP_400_BAD_REQUEST
            raise Exception("Catalog does not belong to user.")

        if (entry_exists(user_id, catalog_name, entry.title)):
            response.status_code = status.HTTP_400_BAD_REQUEST
            raise Exception("Entry already exists.")
        
        if (not book_doesnt_exist(entry.title, entry.author)):
            response.status_code = status.HTTP_400_BAD_REQUEST
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
        return "Failed to create entry"

    return "OK"

class update_book_entries(BaseModel):
    opinion: str
    rating: float
    read_again: bool

@router.put("/{entry_title}")
def update_entry(user_id: int, catalog_name: str, entry_title: str, entry: update_book_entries, response: Response):
    """Given a existing tuple of user_id, catalog_name, and entry_title you can update the values of that entry.\\
        Note that date_read must be of the form \"YYYY-MM-DD\""""
    # update any value of the specified entry

    try:
        if (not catalog_belongs_to_user(user_id, catalog_name)):
            response.status_code = status.HTTP_400_BAD_REQUEST
            raise Exception("Catalog does not belong to user.")

        if (not entry_exists(user_id, catalog_name, entry_title)):
            response.status_code = status.HTTP_400_BAD_REQUEST
            raise Exception("Entry does not exist.")

        with db.engine.begin() as connection:

            # Get catalog id
            catalog_id = connection.execute(sqlalchemy.text(
                """
                SELECT
                    id
                FROM
                    catalogs
                WHERE
                    user_id = :user_id and
                    name = :catalog_name
                """
            ), {"user_id": user_id, "catalog_name": catalog_name}).one()
            parameters = entry.dict()
            parameters.update({"entry_title": entry_title})
            parameters.update({"catalog_id": catalog_id.id})

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
                        WHERE book_title = :entry_title and catalog_id = :catalog_id
                    )
                """
            ), parameters)
    
        response.status_code = status.HTTP_202_ACCEPTED
        return f"Entry '{entry_title}' updated successfully"

    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return f"Error: {e}"

@router.delete("/{entry_title}")
def delete_entry(user_id: int, catalog_name: str, entry_title: str, response: Response):
    """Given a existing tuple of user_id, catalog_name, and entry_title you can delete that entry."""
    # DELETE FROM entries specified title

    try:
        if (not catalog_belongs_to_user(user_id, catalog_name)):
            response.status_code = status.HTTP_400_BAD_REQUEST
            raise Exception("Catalog does not belong to user.")
        
        if (not entry_exists(user_id, catalog_name, entry_title)):
            response.status_code = status.HTTP_400_BAD_REQUEST
            raise Exception("Entry does not exist.")

        with db.engine.begin() as connection:
            # Get catalog id
            catalog_id = connection.execute(sqlalchemy.text(
                """
                SELECT
                    id
                FROM
                    catalogs
                WHERE
                    user_id = :user_id and
                    name = :catalog_name
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
                        JOIN book_entry ON book_entry.entry_id = entries.id
                        JOIN books on books.id = book_entry.book_id
                        WHERE book_title = :entry_title and catalog_id = :catalog_id
                    )
                """
            ), {"entry_title": entry_title, "catalog_id": catalog_id.id})
        response.status_code = status.HTTP_202_ACCEPTED
        return f"Entry '{entry_title}' deleted successfully"

    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return f"Error: {e}"