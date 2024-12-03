# Peer Review Responses
### Lucas Pierce Endpoint Testing Responses
- **Response to Catalog 500 Errors:**  Error handling has been appropriately and correctly added to all catalog endpoints
- **Response to PUT/DELETE on Entry Endpoints:**  `PUT` and `DELETE` requests now only work when the user provides a valid catalog entry belonging to the user and will throw an error response otherwise
    - For example: `PUT` or `DELETE` `/users/{user_id}/catalogs/{catalog_name}/game-entries/{entry_title}` will no longer say "OK" to bad input
- **Response to Following Issues:** Following now handles when users try to follow themselves or people they already follow with a correct error response
- **Response to Search Endpoint Issues:** All search endpoints have been renamed and work like regular queries now

### Lucas Pierce Code Review Responses
- **Response to admin.py Review:** If a command fails, it throws a HTTP 500 error and prints to console which command failed, else if all goes well, HTTP 201 is sent as a response
- **Response to {}_entries.py Review:** Input validation and HTTP status codes have been implemented for these endpoints
- **Response to catalogs.py Review:** All endpoints have been renamed to follow RESTful practices, 409 is returned upon conflicting catalog names, validation has been added to `PUT` endpoint, `/search` is now a proper `GET` query
-  **Response to datasets.py Review:** This file has been refactored into games.py, movies.py, etc as recommended
- **Response to followers.py Review:** This file has been renamed to following.py and enpoints now have `/followees` as a prefix (ex: `GET /users/{user_id}/followees`), error handling and validation have been added to all endpoints with proper HTTP response statuses such that a user can no longer follow themselves, follow people they already follow, delete a followee that they do not follow, etc

### Corbyn Rasque Code Review Responses
- **Response to Issue 1: Transaction Buildup:** We’ve collected all errorhandling into a set of function calls in supabase that can be called in one transaction. Ex: “SELECT func1() AS val1, func2() AS val2…” As such we can have as many checks as we want with only one transaction.
- **Response to Issue 2: Data Marshalling:** While this would work and would reduce duplicated dictionary entries, I think each entry type could become more different in the future to the point that using the same base dictionary for each type could hurt future development. Already, trying to do anything universal with all entry types is difficult. Tying them together in any way would only cause harm.
- **Response to Issue 3: Multiple Identical Calls:** Yes, this would work and would likely use materialized views, however, we would need to keep track of what the search was and if the same search is being done again. Also making for future proofing that the view is updated is important. Ultimately, this endpoint is not resource intensive currently and the time for implementing this feature could be better spent.
- **Response to Issue 4: Search Ordering:** Fixed, however, This did cause us to implement some duplicate code (A for loop in each search endpoint appending not used order by columns to the search.), in favor of time, we have not abstracted/consolidated this code
- **Response to Issue 5: URL Naming Convention:** We’ve renamed the URLs to not include search. They also better follow a hierarchy. I’m not concerned about the length of the URLs and changing game-entries to entries/games or games might be more ambiguous and difficult to follow.
- **Response to Issue 6: Extraneous Queries for Error Handling:** Both issues resolved. One with .rowcount the other by not double defining a dictionary.
- **Respones to Issue 7: Inconsistent Exception Handling:** We have made a lot of improvements to exception handling and errors with status codes are now properly being returned in responses
- **Respones to Issue 8: Separation of Concerns:** I believe this endpoint is fundamentally flawed. I either think we need to rework each type of entry in our schema to be better related to each other or not have a single endpoint that searches all type of entries limited to one type at a time. With that said properly fixing this endpoint would take a larger reworking that we don’t have time for.
- **Respones to Issue 9: Code Duplication:** We are no longer using game_entry.recommend
- **Respones to Issue 10: ON CONFLICT / DO USE:** We have implemented the `ON CONFLICT DO NOTHING` as Corbyn suggested.
- **Respones to Issue 11: COALESCE Use:** This is a good idea and is now implemented where applicable in searching endpoints.
- **Respones to Issue 12: SQL Injection Risks:** For the sake of this class, we are not worried about SQL injection with our current implementaions of query builder and parameter binding.

### Corbyn Rasque Schema/API Design Comment Responses
- **Response to Comment 1: Social Table Delete Cascade:** Agreed and fixed. There is now a foreign key on follower_id which cascades on updates and deletes.
- **Response to Comment 2: Username Uniqueness & Nullity:** Agreed and fixed. Usernames can no longer be null.
- **Response to Comment 3: Catalog Ownership:** Agreed and fixed. user_id for catalogs can no longer be null.
- **Response to Comment 4: Catalog Name Uniqueness:** Agreed and fixed. Catalog names can no longer be null. The code no longer treats catalog names as being uniqueness. Now (catalog name, type) pairings are unique per user.
- **Response to Comment 5: Book Entry Nullity:** Agreed and fixed. Book_id can no longer be null.
- **Response to Comment 6: Game Entry Nullity:** Agreed and fixed. Game_id can no longer be null.
- **Response to Comment 7: Movie Entry Nullity:** Agreed and fixed. Movie_id can no longer be null.
- **Response to Comment 8: Empty String Default Value:** Agreed and fixed. However the title for others should be forced to not be null.
- **Response to Comment 9: URL Length & REST:** We’ve made changes to our URLs to obey the RESTful syntax. Such as getting rid of search at the end of some urls. As for changing recommendations to `user/{user_id}/catalogs/{catalog}/recommendations` I don’t see how this would differentiate between one’s own recommended versus the recommended of others. Thus I believe starting anything to do with social as `/users/{user_id}/followees` to be better as now we are looking at a list of users you are following.
- **Response to Comment 10: Media Search Punctuation:** We see this inconvenience and think a better search than ILIKE would be nice. The proper way to implement this would be to use a fuzzysearch type library. This would allow the user to even miss spell titles and authors and still find what they are looking for. Again, in the interest of time, we will not implement this recommendation.
- **Response to Comment 11: Follow User Not Working:** It is possible that Corbyn was misusing the endpoint, regardless, we have made it more clear how to use each endpoint with docstrings.
- **Response to Comment 12: Catalog Creation Not Working:** It is possible that Corbyn was misusing the endpoint, regardless, we have made it more clear how to use each endpoint with docstrings.

### Angelika Canete Code Review Responses
- **Response to Issue 1: API Spec Mismatch:** API Spec and code now match.
- **Response to Issue 2: Remove Unnecessary Comments:** Done.
- **Response to Issue 3: Delete Users:** Now a user must exist in order to be deleted. For the sake of our project a user_id can be replaced with the idea of some sort of authentication or login that only the owner would have access to. In this sense you can’t delete another user’s account.
- **Response to Issue 4: Following Users that are Already Followed:** `POST` and `DELETE` `/users/{user_id}/followees` now uses nested select statements to catch problems with following other users and removing people as followees
- **Response to Issue 5: Switch Join Statement:** Addressed by changes made in response to issue 4.
- **Response to Issue 6: Implement WITH Statement:** Addressed by changes made in response to issue 4. 
- **Response to Issue 7: Use scalar_one():** Agreed and fixed. 
- **Response to Issue 8: Another API Spec Mismatch:** API Spec and code now match. 
- **Response to Issue 9: Fix Broken Endpoint:** This was an incomplete endpoint. It has now been replaced by `GET /users/{user_id}/followees/entries` where query parameters can be used to specify only recommended entries.
- **Response to Issue 10: Remove Another Unnecessary Comment:** Done.
- **Response to Issue 11: Consistency Across Files:** We are going to ignore any minor inconsistencies. Most files are consistent and any minor inconsistencies in formatting/styling would be caught by a linter/style checker if one was implemented.
- **Response to Issue 12: Unable to Create Catalog:** The type of “video game” is an invalid type for a catalog, it should be “games”. We’ve updated the APISpec and the endpoints in /docs to clarify the use of all endpoints.
- **Response to Issue 13: Refactor Multiple DB Calls:** We have addressed this by creating functions in postgres for making these checks and simply call that function in postgres.
- **Response to Issue 14: Update v1 Test Document:** v1_manual_test updated with new endpoints and req/res bodies.
- **Response to Issue 15: Update v2 Test Document:** v2_manual_test updated with new endpoints and req/res bodies.
- **Response to Issue 16: 500 Internal Server Error When Following a User:** This error now returns 404 "User with requested username does not exist.".

### Angelika Canete Schema/API Design Comment Responses
- **Response to Comment 1: users.id Column Change:** users.id is the column whereas users.user_pkey is the constraint in the schema. 
- **Response to Comment 2: Book ID Nullity:** Book IDs can no longer be null.
- **Response to Comment 3: Input Validation for Ratings:** Entry ratings are now properly validated so that they must be within a scale of 0-10.
- **Response to Comment 4: Endpoint Rename Suggestion:** All endpoints have been renamed to reflect RESTful best practices.
- **Response to Comment 5: Add Request Body to DELETE:** The URL contains all required info, so there is no need for a req body.
- **Response to Comment 6: Double Check req/res Bodies Are in API Spec:** Yes, all necessary req/res bodies have been added to the API spec, however, for searching endpoints we’ve described the structure of the JSON response instead of giving an actual response.
- **Response to Comment 7: movies.id Column Change:** Same issue as comment 1.
- **Response to Comment 8: Require date_seen Attribute:** Most fields for specific entries other than Title shouldn’t be required as this could be cumbersome for some people. Perhaps someone remembers seeing a movie however not enough to give it much of a rating or to know when they saw it.
- **Response to Comment 9: Add HTTP Response Codes:** All endpoints now have proper HTTP response codes being sent.
- **Response to Comment 10: Fix Delete Endpoint Name:** All endpoints now follow best RESTful practices.
- **Response to Comment 11: Fix Create Endpoint Name:** Same issue as comment 10.
- **Response to Comment 12: Add field to API Spec:** The API Spec now matches our code.