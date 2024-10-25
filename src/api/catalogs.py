from fastapi import APIRouter
from src import database as db

router = APIRouter(
    prefix="/catalogs",
    tags=["catalogs"],
)

@router.post("user/{user_id}/catalogs")
def create_catalog():
    return "OK"

@router.get("user/{user_id}/catalog/search")
def search_catalogs():
    return "OK"

@router.post("user/{user_id}/catalogs")
def create_catalog():
    return "OK"

@router.post("user/{user_id}/catalogs")
def create_catalog():
    return "OK"