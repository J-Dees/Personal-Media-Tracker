from fastapi import APIRouter, Response, status
import sqlalchemy
from src import database as db
import os
import re

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

def parse_csv(file_name: str) -> list[dict]:
    append_dict = []
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(root_dir, file_name)
    with open(file_path, "r") as file:
        header = file.readline().strip().split(',')
        header = [h.strip("'ï»¿'") for h in header]
        header = [h.strip('"') for h in header]
        #print(header)
        for line in file:
            line_parts = re.split(r',(?=")', line)
            line_parts = [line.strip() for line in line_parts]
            line_parts = [line.strip('"') for line in line_parts]
            append_dict.append(
                {
                    f"{header[0]}": int(line_parts[0]),
                    f"{header[1]}": f"{line_parts[1]}",
                    f"{header[2]}": int(line_parts[2]) if line_parts[2].isdigit() else f"{line_parts[2]}"
                    
                })
    return append_dict

@router.post("/reset")
def reset_db(response: Response):
    '''
    Please never actually use this.
    It takes a while to insert all of the data into the tables.
    '''

    # books = parse_csv("books_data.csv")
    # movies = parse_csv("movies_data.csv")
    # games = parse_csv("games_data.csv")

    # try:
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            SELECT 
                delete_database(),
                create_database()
            """))
    # connection.execute(sqlalchemy.text("SELECT create_database()"))
    #         book_res = connection.execute(sqlalchemy.text("INSERT INTO books (id, book_title, author) VALUES (:id, :book_title, :author)"), books)
    #         movie_res = connection.execute(sqlalchemy.text("INSERT INTO movies (id, movie_title, year) VALUES (:id, :movie_title, :year)"), movies)
    #         games_res = connection.execute(sqlalchemy.text("INSERT INTO games (id, game_title, year) VALUES (:id, :game_title, :year)"), games)

    #     if book_res.rowcount != len(books):
    #         response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    #         raise Exception("Did not insert all books")

    #     if movie_res.rowcount != len(movies):
    #         response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    #         raise Exception("Did not insert all movies")

    #     if games_res.rowcount != len(movies):
    #         response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    #         raise Exception("Did not insert all games")

    #     response.status_code = status.HTTP_201_CREATED
        return {"status": "Reset finished"}
    # except Exception as e:
    #         print("Reset failed", e)
    #         return {"status": "Reset failed"}