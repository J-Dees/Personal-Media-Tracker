from fastapi import APIRouter

router = APIRouter(
    prefix="/user_functions",
    tags=["user functions"],
)

@router.post("user/create")
def create_new_user():
    # INSERT user into user list with unique name, returning the id generated for that user
    # we should probably also login the user after they create an account for simplicity
    return "OK"

@router.get("user/login")
def login_user():
    # verify that the username exists and return a successful login message, allow access to catalogs for that user
    return "OK"

@router.delete("user/{user_id}")
def delete_user():
    # remove user with passed id from user table
    return "OK"