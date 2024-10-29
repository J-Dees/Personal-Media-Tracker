from fastapi import APIRouter
import sqlalchemy
from src import database as db
import os

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
        for line in file:
            line_parts = line.strip().split(',')
            for part in line_parts:
                part.strip("'")
            print(line_parts)
            append_dict.append(
                {
                    f"{header[0]}": int(line_parts[0]),
                    f"{header[1]}": f"{line_parts[1]}",
                    f"{header[2]}": int(line_parts[2]) if line_parts[0].isdigit() else f"{line_parts[2]}"
                    
                })
    return append_dict

@router.post("/reset")
def reset_db():
    books = parse_csv("books_data.csv")
    movies = parse_csv("movies_data.csv")
    games = parse_csv("games_data.csv")
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("SELECT delete_database()"))
        connection.execute(sqlalchemy.text("SELECT create_database()"))
        connection.execute(sqlalchemy.text("INSERT INTO books (id, book_title, author) VALUES (:id, :book_title, :author)"), books)
        connection.execute(sqlalchemy.text("INSERT INTO movies (id, movie_title, year) VALUES (:id, :movie_title, :year)"), movies)
        connection.execute(sqlalchemy.text("INSERT INTO games (id, game_title, author) VALUES (:id, :game_title, :year)"), games)
        

@router.post("/load")
def load_data():
    with db.engine.being() as connection:
        connection.execute(sqlalchemy.text("SELECT load_database()"))
            