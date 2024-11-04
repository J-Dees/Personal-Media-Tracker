from enum import Enum
from typing import Optional
from fastapi import APIRouter, Response, status
import sqlalchemy
from pydantic import BaseModel
from src import database as db

router = APIRouter(
    prefix="/data_sets",
    tags=["data_sets"],
)

#defines the max entries per page.
MAX_PER_PAGE = 25
#defines enumerated datatypes of different possible columns to sort by.
class sort_col_books(str, Enum):
    book_title = 'book_title'
    author = 'author'
class sort_col_movies(str, Enum):
    movie_title = 'movie_title'
    year = 'year'
class sort_col_games(str, Enum):
    game_title = 'game_title'
    year = 'year'

@router.get("/books/search")
#                   default page 1, default book_title and author are all, default sorting column is book_title.
def search_books(page: int = 1, book_title: str = "", author: str = "", sort_col: sort_col_books = sort_col_books.book_title):
    """
    Search the books database.
    - book_title only needs to be contained within an actual title.
    - author only needs to be part of the whole author's name.
    """
    #Search books for a book that contains a str sequence in the title and a str sequence in the auhtor.
    #Search gives results in pages with length MAX_PER_PAGE.

    #collect metadata for books table
    metadata_obj = sqlalchemy.MetaData()
    books = sqlalchemy.Table("books", metadata_obj, autoload_with=db.engine)
    #Create stats query for collecting information about the search.
    stats_statement = (
            sqlalchemy.select(
                 sqlalchemy.func.count(books.c.id).label("total_rows"))
            .where(books.c.book_title.ilike(f"%{book_title}%"))
            .where(books.c.author.ilike(f"%{author}%"))
        )   
    #Create a content query that will collect all needed information from the search.
    content_statement = (
        sqlalchemy.select(
            books.c.book_title,
            books.c.author)
        .where(books.c.book_title.ilike(f"%{book_title}%"))
        .where(books.c.author.ilike(f"%{author}%"))
        .limit(MAX_PER_PAGE).offset(MAX_PER_PAGE*(page-1))
        .order_by(sort_col)
    )
    with db.engine.begin() as connection:
        stats = connection.execute(stats_statement).fetchone()
        content = connection.execute(content_statement).mappings().fetchall()

    return {
        'page': page,
        #only show there is a page if there are results.
        'max_page': 0 if stats.total_rows == 0 else (stats.total_rows//MAX_PER_PAGE)+1,
        'content': content
    }

@router.get("/movies/search")
#                   default page 1, default movie_title and year are all, default sorting column is movie_title.
def search_movies(page: int = 1, movie_title: str = "", year: int = None, sort_col: sort_col_movies = sort_col_movies.movie_title):
    """
    Search the movies database.
    - movie_title only needs to be contained within an actual title.
    - year must be the exact date of release.
    """
    #Search books for a book that contains a str sequence in the title and a str sequence in the auhtor.
    #Search gives results in pages with length MAX_PER_PAGE.

    #collect metadata for movies table
    metadata_obj = sqlalchemy.MetaData()
    movies = sqlalchemy.Table("movies", metadata_obj, autoload_with=db.engine)
    #Create stats query for collecting information about the search.
    stats_statement =(
        sqlalchemy.select(
            sqlalchemy.func.count(movies.c.id).label("total_rows")
        )
        .where(movies.c.movie_title.ilike(f'%{movie_title}%'))
    )
    #Create a content query that will collect all needed information from the search.
    content_statement = (
        sqlalchemy.select(
            movies.c.movie_title,
            movies.c.year)
        .where(movies.c.movie_title.ilike(f"%{movie_title}%"))
        .limit(MAX_PER_PAGE).offset(MAX_PER_PAGE*(page-1))
        .order_by(sort_col)
    )

    if year != None: #only searach by year if one is given.
        stats_statement = stats_statement.where(movies.c.year == year)
        content_statement = content_statement.where(movies.c.year == year)

    with db.engine.begin() as connection:
        stats = connection.execute(stats_statement).fetchone()
        content = connection.execute(content_statement).mappings().fetchall()

    return {
        'page': page,
        #only show there is a page if there are results.
        'max_page': 0 if stats.total_rows == 0 else (stats.total_rows//MAX_PER_PAGE)+1,
        "content": content
    }

@router.get("/games/search")
#                   default page 1, default game_title and year are all, default sorting column is game_title.
def search_games(page: int = 1, game_title: str = "", year: int = None, sort_col: sort_col_games = sort_col_games.game_title):
    """
    Search the games database.
    - game_title only needs to be contained within an actual title.
    - year must be the exact date of release.
    """
    #Search books for a book that contains a str sequence in the title and a str sequence in the auhtor.
    #Search gives results in pages with length MAX_PER_PAGE.

    #collect metadata for games table
    metadata_obj = sqlalchemy.MetaData()
    games = sqlalchemy.Table("games", metadata_obj, autoload_with=db.engine)
    #Create stats query for collecting information about the search.
    stats_statement =(
        sqlalchemy.select(
            sqlalchemy.func.count(games.c.id).label("total_rows")
        )
        .where(games.c.game_title.ilike(f'%{game_title}%'))
    )
    #Create a content query that will collect all needed information from the search.
    content_statement = (
        sqlalchemy.select(
            games.c.game_title,
            games.c.year)
        .where(games.c.game_title.ilike(f"%{game_title}%"))
        .limit(MAX_PER_PAGE).offset(MAX_PER_PAGE*(page-1))
        .order_by(sort_col)
    )

    if year != None: #only searach by year if one is given.
        stats_statement = stats_statement.where(games.c.year == year)
        content_statement = content_statement.where(games.c.year == year)

    with db.engine.begin() as connection:
        stats = connection.execute(stats_statement).fetchone()
        content = connection.execute(content_statement).mappings().fetchall()

    return {
        'page': page,
        #only show there is a page if there are results.
        'max_page': 0 if stats.total_rows == 0 else (stats.total_rows//MAX_PER_PAGE)+1,
        "content": content
    }