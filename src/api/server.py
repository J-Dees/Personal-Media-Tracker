from fastapi import FastAPI
from src.api import game_entries, movie_entries, book_entries, other_entries
from src.api import catalogs, entries, following, user_functions, admin, data_sets

description = """ Track your stuff ! """

app = FastAPI(
    title="Personal Media Tracker",
    description=description
)

app.include_router(catalogs.router)
app.include_router(game_entries.router)
app.include_router(movie_entries.router)
app.include_router(book_entries.router)
app.include_router(other_entries.router)
app.include_router(following.router)
app.include_router(user_functions.router)
app.include_router(admin.router)
app.include_router(data_sets.router)

@app.get("/")
async def root():
    return {"message": "Welcome to our Personal Media Tracker"}