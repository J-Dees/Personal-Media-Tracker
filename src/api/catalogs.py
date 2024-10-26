from fastapi import APIRouter
import sqlalchemy
from pydantic import BaseModel
from src import database as db

router = APIRouter(
    prefix="/catalogs",
    tags=["catalogs"],
)

class catalog_create(BaseModel):
    name: str
    type: str
    private: bool

@router.post("user/{user_id}/catalogs")
def create_catalog(user_id: int, entry: catalog_create):
    # insert into the users catalogs a new catalog with a unqiue catalog id

    entry_dict = entry.dict()
    entry_dict.update({"user_id": user_id})
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
                                           INSERT INTO catalogs (user_id, name, type, private) 
                                           VALUES (:user_id, :name, :type, :private)"""), entry_dict)
    return "OK"

@router.get("user/{user_id}/catalogs/search")
def search_catalogs(user_id: int):
    # SELECT all catalogs from the user.
    with db.engine.begin() as connection:
        catalog_entries = connection.execute(sqlalchemy.text("""
                                           SELECT id, name, type, private 
                                           FROM catalogs
                                           WHERE user_id = :user_id"""), {"user_id": user_id}).mappings().fetchall()

    return catalog_entries

@router.delete("user/{user_id}/catalogs")
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


class catalog_update(BaseModel):
    name: str
    private: bool

@router.put("user/{user_id}/catalogs")
def update_catalog(user_id: int, catalog_id: int, catalog_update: catalog_update):
    # update name/type of catalog with catalog id passed by user
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""UPDATE catalogs
                                           SET name = :name,
                                           private = :private"""), catalog_update.dict())
    
    return "OK"