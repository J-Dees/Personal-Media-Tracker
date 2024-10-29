from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

def parse_csv(file_name: str) -> []:
    append_dict = []
    file = open(file_name, "r")
    header = file.readline().rsplit()
    for line in file:
        line_parts = line.strip("\"").split(",")
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
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("SELECT delete_database()"))
        connection.execute(sqlalchemy.text("SELECT create_database()"))
        connection.execute(sqlalchemy.text("INSERT INTO books (id, book_title, author) VALUES (:id, :book_title, :author)"), parse_csv("Personal-Media-Tracker/books_data.csv"))
        connection.execute(sqlalchemy.text("INSERT INTO movies (id, movie_title, year) VALUES (:id, :movie_title, :year)"), parse_csv("Personal-Media-Tracker/movies_data.csv"))
        connection.execute(sqlalchemy.text("INSERT INTO books (id, game_title, author) VALUES (:id, :game_title, :year)"), parse_csv("Personal-Media-Tracker/games_data.csv"))
        

@router.post("/load")
def load_data():
    with db.engine.being() as connection:
        connection.execute(sqlalchemy.text("SELECT load_database()"))
            