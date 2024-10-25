from fastapi import FastAPI
from src.api import catalogs, entries, following, user_functions

description = """ Track your stuff ! """

app = FastAPI(
    title="Personal Media Tracker",
    description=description
)

app.include_router(catalogs.router)
app.include_router(entries.router)
app.include_router(following.router)
app.include_router(user_functions.router)