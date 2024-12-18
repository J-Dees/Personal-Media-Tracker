from enum import Enum
from fastapi import APIRouter, Response, status
import sqlalchemy
from pydantic import BaseModel
from src import database as db

router = APIRouter(
    prefix="/users/{user_id}/catalogs",
    tags=["catalogs"],
)

class catalog_type(str, Enum):
    any = ""
    books = "books"
    games = "games"
    movies = "movies"
    other = "other"
class catalog_order_by(str, Enum):
    created = "id"
    name = "name"
class asc_desc(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("")
def fetch_user_catalogs(response: Response, 
                    user_id: int, 
                    page: int = 1, 
                    type: catalog_type = catalog_type.any, 
                    order_by: catalog_order_by = catalog_order_by.name, 
                    direction: asc_desc = asc_desc.asc):
    '''Search your list of catalogs. Default will search the entire catalog ordered by name.
        - page: The page of results to return.
        - type: Narrows search to only catalogs of a specific type of entry.
        - order_by: Specifies a value to sort the results by. 
        - direction: The sort order of the results in either `asc` or `desc` order.'''
    #Statement for gathering how many rows will be returned.
    stats_statement = (
        sqlalchemy.select(
            sqlalchemy.func.count(db.catalogs.c.id).label("total_rows"))
            .where(db.catalogs.c.user_id == user_id)
    )
    #Statement for gathering the primary content returned.
    content_statement = (
        sqlalchemy.select(
            db.catalogs.c.name,
            db.catalogs.c.type,
            db.catalogs.c.private)
        .where(db.catalogs.c.user_id == user_id)
        .limit(db.MAX_PER_PAGE).offset(db.MAX_PER_PAGE*(page-1))
    )

    #Append proper order_by to the query.
    if (direction == "desc"):
        content_statement = content_statement.order_by(sqlalchemy.desc(order_by))
    else:
        content_statement = content_statement.order_by(order_by)

    #Break ties by the order of catalog_order_by.
    for item in catalog_order_by:
        if item.value != order_by:
            content_statement = content_statement.order_by(item)

    #add where if searching for a specific catalog type.
    if (type != catalog_type.any):
        content_statement = content_statement.where(db.catalogs.c.type == type)
        stats_statement = stats_statement.where(db.catalogs.c.type == type)

    return db.execute_search(stats_statement, content_statement, page, response)

class catalog_create(BaseModel):
    name: str
    type: str
    private: bool

@router.post("")
def create_catalog(user_id: int, entry: catalog_create, response: Response):
    """Create a catalog. 
        - name: Catalog names must be unique to the user.
        - type: Type must be one of the following values 'books', 'movies', 'games', or 'other'.
        - private: Must be either 'true' or 'false'. 'true' will not allow anyone except you to view the catalog."""
    entry_dict = entry.dict()
    entry_dict.update({"user_id": user_id})
    with db.engine.begin() as connection:
        # Enforces catalog_name/catalog_type uniqueness per user.
        results = connection.execute(sqlalchemy.text(
            """
            INSERT INTO catalogs (user_id, name, type, private) 
            VALUES (:user_id, :name, :type, :private)
            ON CONFLICT DO NOTHING
            """), entry_dict)
        if results.rowcount != 1:
            response.status_code = status.HTTP_409_CONFLICT
            return {"error": "Catalog name already taken. Please choose another name."}    
    response.status_code = status.HTTP_201_CREATED
    return {"response": f"Catalog with name {entry.name} created"}

class catalog_update(BaseModel):
    name: str
    private: bool

@router.put("/{catalog_name}")
def update_catalog(user_id: int, catalog_name: str, catalog_update: catalog_update, response: Response):
    """Updates a catalog name and privacy.
        - You must provide a correct user_id and catalog_name pair."""
    catalog_update_dict = catalog_update.dict()
    catalog_update_dict.update({"user_id": user_id,
                                "old_name": catalog_name})

    with db.engine.begin() as connection:
        results = connection.execute(sqlalchemy.text(
            """
            UPDATE catalogs
            SET name = :name, private = :private
            WHERE (user_id, id) = (
                SELECT user_id, id
                FROM catalogs
                WHERE user_id = :user_id AND name = :old_name)
            """), catalog_update_dict)
    if results.rowcount != 1:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"The catalog {catalog_name} does not exist for the user_id {user_id}"}
    response.status_code = status.HTTP_202_ACCEPTED
    return {"repsonse": f"Catalog {catalog_name} updated to {catalog_update}"}
    

@router.delete("/{catalog_name}")
def delete_catalog(user_id: int, catalog_name: str, response: Response):
    """Deletes a catalog and all of its entries.
        - You must provide a valid user_id and catalog_name pair."""
    entry = {
        "user_id": user_id,
        "name": catalog_name
    }
    try:
        with db.engine.begin() as connection:
            catalog = connection.execute(sqlalchemy.text(
                """ 
                SELECT user_id, id
                FROM catalogs
                WHERE user_id = :user_id AND name = :name
                """), entry).one()
            connection.execute(sqlalchemy.text(
                """
                DELETE FROM catalogs
                WHERE (user_id, id) = (:user_id, :id)
                """), {'user_id': catalog.user_id, 'id': catalog.id})
        response.status_code = status.HTTP_204_NO_CONTENT
        return {"response": f"Catalog {catalog_name} successfully deleted"}
    except:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"Unable to find the catalog {catalog_name} for the user with id: {user_id}"}