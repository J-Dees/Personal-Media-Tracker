from enum import Enum
from typing import Optional
from fastapi import APIRouter, Response, status
import sqlalchemy
from pydantic import BaseModel
from src import database as db

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
)

class sort_col_movies(str, Enum):
    movie_title = 'movie_title'
    year = 'year'

@router.get("")
#                   default page 1, default movie_title and year are all, default sorting column is movie_title.
def search_movies(response: Response,
                  page: int = 1, 
                  movie_title: str = "", 
                  year: int = None, 
                  sort_col: sort_col_movies = sort_col_movies.movie_title):
    """
    Search the movies database.
    - page: The page of results to return.
    - movie_title: A String that each movie_title returned must contain.
    - year: must be the exact year of release.
    - sort_col: Specifies a value to sort the results by. 
    """
    #Search books for a book that contains a str sequence in the title and a str sequence in the auhtor.
    #Search gives results in pages with length MAX_PER_PAGE.

    #Create stats query for collecting information about the search.
    stats_statement =(
        sqlalchemy.select(
            sqlalchemy.func.count(db.movies.c.id).label("total_rows")
        )
        .where(db.movies.c.movie_title.ilike(f'%{movie_title}%'))
        .where(db.movies.c.year == sqlalchemy.func.coalesce(year, db.movies.c.year)) 
    )
    #Create a content query that will collect all needed information from the search.
    content_statement = (
        sqlalchemy.select(
            db.movies.c.movie_title,
            db.movies.c.year)
        .where(db.movies.c.movie_title.ilike(f"%{movie_title}%"))
        .where(db.movies.c.year == sqlalchemy.func.coalesce(year, db.movies.c.year)) 
        .limit(db.MAX_PER_PAGE).offset(db.MAX_PER_PAGE*(page-1))
        .order_by(sort_col)
    )

    #Break ties by the order of sort_col_movies.
    for item in sort_col_movies:
        if item.value != sort_col:
            content_statement = content_statement.order_by(item)

    return db.execute_search(stats_statement, content_statement, page, response)