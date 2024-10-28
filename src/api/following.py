from fastapi import APIRouter

router = APIRouter(
    prefix="/user",
    tags=["following"],
)

@router.post("/{user_id}/social")
def add_follower():
    # add a follower by name, INSERT the user_id/follower_id pair into social table
    return "OK"

@router.get("/{user_id}/social/search")
def search_follower():
    # searches through a user's followers based on query
    return "OK"

@router.delete("/{user_id}/social/{follower_id}")
def remove_follower():
    # DELETE FROM social the user_id/follower_id pair
    return "OK"

@router.get("/{user_id}/social/{follower_id}/catalogs")
def view_follower_catalogs():
    # view a specified follower's catalogs
    return "OK"

@router.get("/{user_id}/social/{follower_id}/catalogs/{catalog}/recommendations")
def get_recommended():
    # view all catalog entries that are flagged as recommended in a given follower catalog
    # this is probably something we can implement into a user's own catalogs as well
    return "OK"

@router.get("/{user_id}/social/search/{title}")
def search_catalogs():
    # searches (all ?) follower catalogs for a specified catalog title
    return "OK"
