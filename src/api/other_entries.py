from enum import Enum
from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from datetime import date


router = APIRouter(
    prefix="/users/{user_id}/catalogs/{catalog_name}/other-entries",
    tags=["other_entries"],
)

class other_entries(BaseModel):
    title: str
    description: str
    price: float
    quality: str
    date_obtained: date
    recommend: bool
    private: bool

class entries_order_by(str, Enum):
    title = "title"
    price = "price"
    quality = "quality"
    date_obtained = "date_obtained"
class asc_desc(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("")
def entry_search(user_id: int, 
                 catalog_name: str,
                 response: Response,
                 page: int = 1, 
                 opinion: str = "",
                 order_by: entries_order_by = entries_order_by.title,
                 direction: asc_desc = asc_desc.asc):
    """Search one of your catalog's other_entries. Note that the catalog must be of the other type.
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
        .join(db.other_entry, db.entries.c.id == db.other_entry.c.entry_id)
        .where(db.catalogs.c.user_id == user_id)
        .where(db.catalogs.c.name == catalog_name)
        .where(db.catalogs.c.type == "other")
        .where(db.other_entry.c.description.ilike(f"%{opinion}%"))
    )
    #Statement for gathering the primary content returned.
    content_statement = (
        sqlalchemy.select(
            db.other_entry.c.title,
            db.entries.c.private,
            db.entries.c.recommend,
            db.other_entry.c.quality,
            db.other_entry.c.price,
            db.other_entry.c.date_obtained,
            db.other_entry.c.description)
        .select_from(db.entries)
        .join(db.catalogs, db.entries.c.catalog_id == db.catalogs.c.id)
        .join(db.other_entry, db.other_entry.c.entry_id == db.entries.c.id)
        .where(db.catalogs.c.user_id == user_id)
        .where(db.catalogs.c.name == catalog_name)
        .where(db.catalogs.c.type == "other")
        .where(db.other_entry.c.description.ilike(f"%{opinion}%"))
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
def create_other_entry(user_id: int, catalog_name: str, entry: other_entries, response: Response):
    '''
    Cretes a new other_entry in the catalog catalg_name.\\ 
    The entry must not already exist and the catalog must be of the Type 'other'
        - title: Must be a unique title to the catalog.
        - description: A string describing the entry.
        - quality: A string describing quality (Note: can still be a numaric 0-10) 
        - date_obtained: The date the entry was made or item obtained. Must be of the form "YYYY-MM-DD".
        - recommend: A boolean ('true' or 'false') on whether you would recommend the entry to another person.
        - private: A boolean ('true' or 'false') on if you want others to see this entry.
    '''
    # insert into catalog table a new row with unqiue catalog id
    # do we want this to have a composite key for userid, catalog id, and entry id (ie user 1 catalog 1 entry 1, user 2 catalog 1 entry 1 etc)

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
                    check_catalog_user_relationship(:user_id, :catalog_name, 'other') as catalog_user_relationship,
                    check_entry_in_catalog(:user_id, :catalog_name, 'other', :entry_name) as entry_in_catalog
                """
            ), {"user_id": user_id, "catalog_name": catalog_name, "entry_name": entry.title}).first()

            if (not valid_request.catalog_user_relationship):
                raise Exception("Catalog does not belong to user.")
            
            if (valid_request.entry_in_catalog):
                raise Exception("Entry already exists in catalog.")
        
            entry_id = connection.execute(sqlalchemy.text(
                """
                INSERT INTO
                    entries (catalog_id, private, recommend)
                    (SELECT catalogs.id, :private, :recommend FROM catalogs 
                        WHERE name = :catalog_name 
                        AND user_id = :user_id
                        AND type = 'other')
                RETURNING id
                """
            ), {
                "private": entry.private,
                "recommend": entry.recommend,
                "catalog_name": catalog_name,
                "user_id": user_id
            }).one()

            connection.execute(sqlalchemy.text(
                """
                INSERT INTO
                    other_entry (entry_id, title, description, price, quality, date_obtained)
                VALUES
                    (:entry_id, :title, :description, :price, :quality, :date_obtained)
                """
            ), {
                "entry_id": entry_id.id,
                "title": entry.title,
                "description": entry.description,
                "price": entry.price,
                "quality": entry.quality,
                "date_obtained": entry.date_obtained
            })
    
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": f"{e}"}

    response.status_code = status.HTTP_201_CREATED
    return {"response": "Other entry created."}

class update_other_entries(BaseModel):
    description: str
    price: float
    quality: str

@router.put("/{entry_title}")
def update_entry(user_id: int, catalog_name: str, entry_title: str, entry: update_other_entries, response: Response):
    """Given a existing tuple of user_id, catalog_name, and entry_title you can update the values of that entry.\\
        Note that date_obtained must be of the form \"YYYY-MM-DD\""""
    # update any value of the specified entry
    print(entry_title)
    try:
        with db.engine.begin() as connection:
            # Checks if:
            # 1. Catalog belongs to user
            # 2. Entry is in catalog
            # Raises exception if there are any conflicts
            valid_request = connection.execute(sqlalchemy.text(
                """
                select 
                    check_catalog_user_relationship(:user_id, :catalog_name, 'other') as catalog_user_relationship,
                    check_entry_in_catalog(:user_id, :catalog_name, 'other', :entry_name) as entry_in_catalog
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
                    type = 'other'
                """
            ), {"user_id": user_id, "catalog_name": catalog_name}).one()

            parameters = entry.dict()
            parameters.update({"entry_title": entry_title})
            parameters.update({"catalog_id": catalog_id.id})
            connection.execute(sqlalchemy.text(
                """
                UPDATE
                    other_entry
                SET
                    description = :description,
                    price = :price,
                    quality = :quality
                WHERE entry_id =
                    (
                        SELECT entry_id
                        FROM entries
                        JOIN other_entry ON other_entry.entry_id = entries.id
                        WHERE other_entry.title = :entry_title and catalog_id = :catalog_id
                    )
                """
            ), parameters)
        response.status_code = status.HTTP_202_ACCEPTED
        return {"response": f"Entry '{entry_title}' updated successfully"}

    except Exception as e:
        response.status_code = status.HTTP_404_NOT_FOUND
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
                    check_catalog_user_relationship(:user_id, :catalog_name, 'other') as catalog_user_relationship,
                    check_entry_in_catalog(:user_id, :catalog_name, 'other', :entry_name) as entry_in_catalog
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
                        JOIN other_entry ON other_entry.entry_id = entries.id
                        WHERE other_entry.title = :entry_title and catalog_id = :catalog_id
                    )
                """
            ), {"entry_title": entry_title, "catalog_id": catalog_id.id})
        response.status_code = status.HTTP_202_ACCEPTED
        return f"Entry '{entry_title}' deleted successfully"

    except Exception as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return f"Error: {e}"