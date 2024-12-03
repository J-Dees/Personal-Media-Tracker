from enum import Enum
from typing import Optional
from fastapi import APIRouter, Response, status
import sqlalchemy
from pydantic import BaseModel
from src import database as db

router = APIRouter(
    prefix="/games",
    tags=["games"],
)

#defines enumerated datatypes of different possible columns to sort by.
class sort_col_games(str, Enum):
    game_title = 'game_title'
    year = 'year'

@router.get("")
#                   default page 1, default game_title and year are all, default sorting column is game_title.
def search_games(response: Response,
                 page: int = 1,
                 game_title: str = "", 
                 year: int = None, 
                 sort_col: sort_col_games = sort_col_games.game_title):
    """
    Search the games database.
    - page: The page of results to return.
    - game_title: A String that each game_title returned must contain.
    - year: must be the exact year of release.
    - sort_col: Specifies a value to sort the results by. 
    """
    #Search books for a book that contains a str sequence in the title and a str sequence in the auhtor.
    #Search gives results in pages with length MAX_PER_PAGE.

    #Create stats query for collecting information about the search.
    stats_statement =(
        sqlalchemy.select(
            sqlalchemy.func.count(db.games.c.id).label("total_rows")
        )
        .where(db.games.c.game_title.ilike(f'%{game_title}%'))
        .where(db.games.c.year == sqlalchemy.func.coalesce(year, db.games.c.year)) 
    )
    #Create a content query that will collect all needed information from the search.
    content_statement = (
        sqlalchemy.select(
            db.games.c.game_title,
            db.games.c.year)
        .where(db.games.c.game_title.ilike(f"%{game_title}%"))
        .where(db.games.c.year == sqlalchemy.func.coalesce(year, db.games.c.year)) 
        .limit(db.MAX_PER_PAGE).offset(db.MAX_PER_PAGE*(page-1))
        .order_by(sort_col)
    )

    #Break ties by the order of sort_col_games.
    for item in sort_col_games:
        if item.value != sort_col:
            content_statement = content_statement.order_by(item)

    return db.execute_search(stats_statement, content_statement, page, response)