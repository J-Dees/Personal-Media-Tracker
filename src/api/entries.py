from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/entries",
    tags=["entries"],
)

@router.post("user/{user_id}/catalogs/{catalog_name}/entries")
def create_entry():
    # insert into catalog table a new row with unqiue catalog id
    return "OK"

@router.get("user/{user_id}/catalogs/{catalog_name}/entries/search")
def entry_search():
    # find a specific entry in the current catalog with the given query
    return "OK"

@router.put("user/{user_id}/catalogs/{catalog_name}/entries/{entry_title}")
def update_entry():
    # update any value of the specified entry
    return "OK"

@router.delete("user/{user_id}/catalogs/{catalog_name}/entries/{entry_title}")
def delete_entry():
    # DELETE FROM entries specified title
    return "OK"