from fastapi import APIRouter
from src import database as db

router = APIRouter(
    prefix="/catalogs",
    tags=["catalogs"],
)

@router.post("user/{user_id}/catalogs")
def create_catalog():
    # insert into catalog table a new row with unqiue catalog id
    # do we want this to have a composite key for userid and catalog id (ie user 1 catalog 1, user 2 catalog 1 etc)
    # I think we should, this will make follower catalog lookup easier when a user does social interactions
    return "OK"

@router.get("user/{user_id}/catalogs/search")
def search_catalogs():
    # SELECT from catalog table with requested queries
    return "OK"

@router.delete("user/{user_id}/catalogs")
def delete_catalog():
    # DELETE FROM catalog where catalog id = id passed by user
    return "OK"

@router.put("user/{user_id}/catalogs")
def update_catalog():
    # update name/type of catalog with catalog id passed by user
    return "OK"