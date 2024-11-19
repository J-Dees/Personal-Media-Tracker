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
def search_games(page: int = 1, game_title: str = "", year: int = None, sort_col: sort_col_games = sort_col_games.game_title):
    """
    Search the games database.
    - game_title only needs to be contained within an actual title.
    - year must be the exact date of release.
    """
    #Search books for a book that contains a str sequence in the title and a str sequence in the auhtor.
    #Search gives results in pages with length MAX_PER_PAGE.

    #Create stats query for collecting information about the search.
    stats_statement =(
        sqlalchemy.select(
            sqlalchemy.func.count(db.games.c.id).label("total_rows")
        )
        .where(db.games.c.game_title.ilike(f'%{game_title}%'))
    )
    #Create a content query that will collect all needed information from the search.
    content_statement = (
        sqlalchemy.select(
            db.games.c.game_title,
            db.games.c.year)
        .where(db.games.c.game_title.ilike(f"%{game_title}%"))
        .limit(db.MAX_PER_PAGE).offset(db.MAX_PER_PAGE*(page-1))
        .order_by(sort_col)
    )

    if year != None: #only searach by year if one is given.
        stats_statement = stats_statement.where(db.games.c.year == year)
        content_statement = content_statement.where(db.games.c.year == year)

    return db.execute_search(stats_statement, content_statement, page)