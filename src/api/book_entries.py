from fastapi import APIRouter
from pydantic import BaseModel
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/user",
    tags=["book_entries"],
)

class book_entries(BaseModel):
    title: str
    opinion: str
    rating: float
    hours_played: float
    play_again: bool
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

    # Later: check if catalog belongs to user, duplicates


    return "OK"

        
@router.get("/{user_id}/catalogs/{catalog_name}/book_entries/search")
def entry_search():
    # find a specific entry in the current catalog with the given query
    return "OK"

class update_book_entries(BaseModel):
    opinion: str
    rating: float
    hours_played: float
    play_again: bool
@router.put("/{user_id}/catalogs/{catalog_name}/book_entries/{entry_title}")
def update_entry(user_id: int, catalog_name: str, entry_title: str, entry: update_book_entries):
    # update any value of the specified entry

    # Later, verify catalog belongs to user

    return "OK"

@router.delete("/{user_id}/catalogs/{catalog_name}/book_entries/{entry_title}")
def delete_entry():
    # DELETE FROM entries specified title
    return "OK"