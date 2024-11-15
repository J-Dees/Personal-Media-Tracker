from fastapi import FastAPI
from src.api import game_entries, movie_entries, book_entries, other_entries
from src.api import catalogs, following, user_functions, admin, movies, books, games

description = """ Track your stuff ! """

app = FastAPI(
    title="Personal Media Tracker",
    description=description
)

#User and social Functionality.
app.include_router(user_functions.router)
app.include_router(following.router)
#Creating catalogs.
app.include_router(catalogs.router)
#Game stuff
app.include_router(games.router)
app.include_router(game_entries.router)
#Movie stuff
app.include_router(movies.router)
app.include_router(movie_entries.router)
#Books stuff
app.include_router(books.router)
app.include_router(book_entries.router)
#Other stuff
app.include_router(other_entries.router)
#Admin stuff
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"message": "Welcome to our Personal Media Tracker"}