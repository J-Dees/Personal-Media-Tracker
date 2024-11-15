import os
import dotenv
import sqlalchemy

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")


def execute_search(stats_statement, content_statement, page):
    with engine.begin() as connection:
        stats = connection.execute(stats_statement).fetchone()
        content = connection.execute(content_statement).mappings().fetchall()

    try:
        #If page input is outside of valid range for the search.
        if (page > (stats.total_rows//MAX_PER_PAGE)+1 or page < 1):
            raise Exception(f"page is outside of valid range 1-{(stats.total_rows//MAX_PER_PAGE)+1}")
    except Exception as e:
        print(e)
        return e

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
