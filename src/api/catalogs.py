from enum import Enum
from fastapi import APIRouter, Response, status
import sqlalchemy
from pydantic import BaseModel
from src import database as db

router = APIRouter(
    prefix="/user",
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

@router.get("/{user_id}/catalogs/search")
def search_catalogs(response: Response, 
                    user_id: int, 
                    page: int = 1, 
                    type: catalog_type = catalog_type.any, 
                    order_by: catalog_order_by = catalog_order_by.name, 
                    direction: asc_desc = asc_desc.asc):
    '''Search A user's list of catalogs. Default will search the entire catalog ordered by name.'''
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
    #add where if searching for a specific catalog type.
    if (type != catalog_type.any):
        content_statement = content_statement.where(db.catalogs.c.type == type)
        stats_statement = stats_statement.where(db.catalogs.c.type == type)
    
    return db.execute_search(stats_statement, content_statement, page)

class catalog_create(BaseModel):
    name: str
    type: str
    private: bool

@router.post("/{user_id}/catalogs")
def create_catalog(user_id: int, entry: catalog_create, response: Response):
    # insert into the users catalogs a new catalog with a unqiue catalog id

    entry_dict = entry.dict()
    entry_dict.update({"user_id": user_id})
    with db.engine.begin() as connection:
        exists = connection.execute(sqlalchemy.text("""
                                              SELECT id 
                                              FROM catalogs 
                                              WHERE user_id = :user_id 
                                              AND name = :name"""), 
                                              {
                                                  "user_id": user_id,
                                                  "name": entry.name
                                              }).scalar_one_or_none()
        if exists is None:
            connection.execute(sqlalchemy.text("""
                                               INSERT INTO catalogs (user_id, name, type, private) 
                                               VALUES (:user_id, :name, :type, :private)"""), entry_dict)
            response.status_code = status.HTTP_201_CREATED
            return "OK"
        else:    
            response.status_code = status.HTTP_403_FORBIDDEN
            return "Catalog name already taken. Please choose another name."

class catalog_update(BaseModel):
    name: str
    private: bool

@router.put("/{user_id}/catalogs")
def update_catalog(user_id: int, catalog_id: int, catalog_update: catalog_update):
    # update name/type of catalog with catalog id passed by user
    
    catalog_update_dict =  catalog_update.dict()
    catalog_update_dict.update({"user_id": user_id,
                                "id": catalog_id})
    with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("""UPDATE catalogs
                                           SET name = :name,
                                               private = :private
                                           WHERE user_id = :user_id 
                                           AND id = :id"""), catalog_update_dict)
    
    return "OK"

@router.delete("/{user_id}/catalogs")
def delete_catalog(user_id: int, catalog_id: int):
    # DELETE FROM catalog where catalog id = id passed by user

    entry = {
        "user_id": user_id,
        "id": catalog_id
    }
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(""" 
                                           DELETE FROM catalogs 
                                           WHERE user_id = :user_id AND id = :id"""), entry)
    
    return "OK"