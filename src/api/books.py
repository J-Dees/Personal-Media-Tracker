from enum import Enum
from typing import Optional
from fastapi import APIRouter, Response, status
import sqlalchemy
from pydantic import BaseModel
from src import database as db

router = APIRouter(
    prefix="/books",
    tags=["books"],
)

#defines enumerated datatypes of different possible columns to sort by.
class sort_col_books(str, Enum):
    book_title = 'book_title'
    author = 'author'

@router.get("")
#                   default page 1, default book_title and author are all, default sorting column is book_title.
def search_books(page: int = 1, book_title: str = "", author: str = "", sort_col: sort_col_books = sort_col_books.book_title):
    """
    Search the books database.
    - page: The page of results to return.
    - book_title: A String that each book_title returned must contain.
    - Author: A String that each author returned must contain.
    - sort_col: Specifies a value to sort the results by. 
    """
    #Search books for a book that contains a str sequence in the title and a str sequence in the auhtor.
    #Search gives results in pages with length MAX_PER_PAGE.

    #Create stats query for collecting information about the search.
    stats_statement = (
            sqlalchemy.select(
                 sqlalchemy.func.count(db.books.c.id).label("total_rows"))
            .where(db.books.c.book_title.ilike(f"%{book_title}%"))
            .where(db.books.c.author.ilike(f"%{author}%"))
        )   
    
    #Create a content query that will collect all needed information from the search.
    content_statement = (
        sqlalchemy.select(
            db.books.c.book_title,
            db.books.c.author)
        .where(db.books.c.book_title.ilike(f"%{book_title}%"))
        .where(db.books.c.author.ilike(f"%{author}%"))
        .limit(db.MAX_PER_PAGE).offset(db.MAX_PER_PAGE*(page-1))
        .order_by(sort_col)
    )
    
    return db.execute_search(stats_statement, content_statement, page)
