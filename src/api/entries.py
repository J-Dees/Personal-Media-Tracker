from fastapi import APIRouter
from pydantic import BaseModel
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/user",
    tags=["entries"],
)

class game_entries(BaseModel):
    title: str
    opinion: str
    rating: float
    hours_played: float
    play_again: bool
    recommend: bool
    private: bool

@router.post("/{user_id}/catalogs/{catalog_name}/game_entries")
def create_game_entry(user_id: int, catalog_id: str, entry: game_entries):
    '''
    1.  Identify type of entry from catalog type
    2.  Look up id from game/book/movie
    3.  Insert into game_entry/book_entry... etc.
    4.  Insert game_entry/book_entry... etc. reference to entries
    '''
    # insert into catalog table a new row with unqiue catalog id
    # do we want this to have a composite key for userid, catalog id, and entry id (ie user 1 catalog 1 entry 1, user 2 catalog 1 entry 1 etc)

    # Later: check if catalog belongs to user, duplicates

    with db.engine.begin() as connection:
        entry_id = connection.execute(sqlalchemy.text(
            """
                INSERT INTO entries
                (catalog_id, private, recommend) VALUES (:id, :private, :rec)
                RETURNING id
            """
        ), {
            "id": catalog_id,
            "private": entry.private,
            "rec": entry.recommend
        }).scalar_one()
        
        game_id = connection.execute(sqlalchemy.text(
        """
            SELECT id
            FROM games
            WHERE game_title = :title
        """
        ), {"title": entry.title}).scalar_one()
        
        connection.execute(sqlalchemy.text(
            """
                INSERT INTO game_entry
                (entry_id, game_id, hours_played, opinion, rating, play_again) 
                VALUES 
                (:entry_id, :game_id, :hours_played, :opinion, :rating, :play_again)
            """
        ),
        {
            "entry_id": entry_id,
            "game_id": game_id,
            "hours_played": entry.hours_played,
            "opinion": entry.opinion,
            "rating": entry.rating,
            "play_again": entry.play_again
        })


    return "OK"

        
@router.get("/{user_id}/catalogs/{catalog_name}/entries/search")
def entry_search():
    # find a specific entry in the current catalog with the given query
    return "OK"
class update_game_entries(BaseModel):
    opinion: str
    rating: float
    hours_played: float
    play_again: bool
@router.put("/{user_id}/catalogs/{catalog_name}/entries/{entry_title}")
def update_entry(user_id: int, catalog_name: str, entry_title: str, entry: update_game_entries):
    # update any value of the specified entry

    # Later, verify catalog belongs to user
    entry_dic = entry.dict()
    entry_dic.update({"entry_title": entry_title})
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            UPDATE game_entry
            SET hours_played = :hours_played, rating = :rating, opinion = :opinion, play_again = :play_again
            WHERE entry_id = 
                (
                SELECT entry_id
                FROM entries
                JOIN game_entry ON game_entry.entry_id = entries.id
                JOIN games on games.id = game_entry.game_id
                WHERE game_title = :entry_title
                )
            """
        ), entry_dic)

    return "OK"

@router.delete("/{user_id}/catalogs/{catalog_name}/game_entries/{entry_title}")
def delete_entry():
    # DELETE FROM entries specified title
    return "OK"