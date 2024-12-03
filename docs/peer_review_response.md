# Lucas Pierce Endpoint Testing Responses
- **Response to Catalog 500 Errors:**  Error handling has been appropriately and correctly added to all catalog endpoints
- **Response to PUT/DELETE on Entry Endpoints:**  `PUT` and `DELETE` requests now only work when the user provides a valid catalog entry belonging to the user and will throw an error response otherwise
    - For example: `PUT` or `DELETE` `/users/{user_id}/catalogs/{catalog_name}/game-entries/{entry_title}` will no longer say "OK" to bad input
- **Response to Following Issues:** Following now handles when users try to follow themselves or people they already follow with a correct error response
- **Response to Search Endpoint Issues:** All search endpoints have been renamed and work like regular queries now

# Lucas Pierce Code Review Responses
- **Response to admin.py Review:** If a command fails, it throws a HTTP 500 error and prints to console which command failed, else if all goes well, HTTP 201 is sent as a response
- **Response to {}_entries.py Review:** Input validation and HTTP status codes have been implemented for these endpoints
- **Response to catalogs.py Review:** All endpoints have been renamed to follow RESTful practices, 409 is returned upon conflicting catalog names, validation has been added to `PUT` endpoint, `/search` is now a proper `GET` query
-  **Response to datasets.py Review:** This file has been refactored into games.py, movies.py, etc as recommended
- **Response to followers.py Review:** This file has been renamed to following.py and enpoints now have `/followees` as a prefix (ex: `GET /users/{user_id}/followees`), error handling and validation have been added to all endpoints with proper HTTP response statuses such that a user can no longer follow themselves, follow people they already follow, delete a followee that they do not follow, etc

