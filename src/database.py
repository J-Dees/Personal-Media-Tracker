import os
import dotenv
import sqlalchemy
from fastapi import Response, status

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")


def execute_search(stats_statement, content_statement, page, response : Response):
    with engine.begin() as connection:
        #get stats and then check if page is outside of a valid range.
        stats = connection.execute(stats_statement).fetchone()
        try:
        #If page input is outside of valid range for the search.
            if (stats.total_rows == 0):
                response.status_code = status.HTTP_404_NOT_FOUND
                raise Exception("No results for your search.")
            if (page > (stats.total_rows//MAX_PER_PAGE)+1 or page < 1):
                response.status_code = status.HTTP_400_BAD_REQUEST
                raise Exception(f"Page is outside of the valid range 1-{(stats.total_rows//MAX_PER_PAGE)+1}")
        except Exception as e:
            return {"error": str(e)}
        content = connection.execute(content_statement).mappings().fetchall()

    return {
        'page': page,
        #only show there is a page if there are results.
        'max_page': 0 if stats.total_rows == 0 else (stats.total_rows//MAX_PER_PAGE)+1,
        "content": content
    }

#Used for searches.
MAX_PER_PAGE = 25

engine = sqlalchemy.create_engine(database_connection_url(), pool_pre_ping=True)
#Collect Metadata.
metadata_obj = sqlalchemy.MetaData()
books = sqlalchemy.Table("books", metadata_obj, autoload_with=engine)
movies = sqlalchemy.Table("movies", metadata_obj, autoload_with=engine)
games = sqlalchemy.Table("games", metadata_obj, autoload_with=engine)
catalogs = sqlalchemy.Table("catalogs", metadata_obj, autoload_with=engine)
entries = sqlalchemy.Table("entries", metadata_obj, autoload_with=engine)
game_entry = sqlalchemy.Table("game_entry", metadata_obj, autoload_with=engine)
movie_entry = sqlalchemy.Table("movie_entry", metadata_obj, autoload_with=engine)
book_entry = sqlalchemy.Table("book_entry", metadata_obj, autoload_with=engine)
other_entry = sqlalchemy.Table("other_entry", metadata_obj, autoload_with=engine)
social = sqlalchemy.Table("social", metadata_obj, autoload_with=engine)
users = sqlalchemy.Table("users", metadata_obj, autoload_with=engine)