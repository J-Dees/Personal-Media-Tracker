from fastapi import APIRouter, Response, status
import sqlalchemy
from pydantic import BaseModel
from src import database as db

router = APIRouter(
    prefix="/user",
    tags=["catalogs"],
)

@router.get("/{user_id}/catalogs/search")
def search_catalogs(user_id: int, response: Response):
    # SELECT all catalogs from the user.
    with db.engine.begin() as connection:
        catalog_entries = connection.execute(sqlalchemy.text("""
                                           SELECT id, name, type, private 
                                           FROM catalogs
                                           WHERE user_id = :user_id"""), {"user_id": user_id}).mappings().fetchall()
    if len(catalog_entries) > 0:
        return catalog_entries
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return "No catalogs found."

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