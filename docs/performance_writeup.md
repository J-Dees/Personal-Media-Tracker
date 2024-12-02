## NOTES:

# Performance write up:
### Entry generation script:
### Explanation:
- 

## Endpoint Performance:
### user_functions
- GET /users
    - 3ms
- POST /users
    - 9 ms
- GET /users/{user_name}
    - 5 ms
- DELETE /users/{user_id}
    - 22 ms

### following
- GET /users/{user_id}/followees
    - 9 ms
- POST /users/{user_id}/followees
    - 9 ms
- GET /users/{user_id}/followees/catalogs
    - 10 ms
- GET /users/{user_id}/followees/entries
    - 131 ms
- GET /users/{user_id}/followees/follow-recommendations
    - 137 ms
- DELETE /users/{user_id}/followees/{user_name}
    - 7 ms

### catalogs
- GET /users/{user_id}/catalogs
    - 6 ms
- POST /users/{user_id}/catalogs
    - 9 ms
- PUT /users/{user_id}/catalogs/{catalog_name}
    - 9 ms
- DELETE /users/{user_id}/catalogs/{catalog_name}
    - 23 ms

### games
- GET /games
    - 16 ms

### game_entries
- GET /users/{user_id}/catalogs/{catalog_name}/game-entries
    - 43 ms
- POST /users/{user_id}/catalogs/{catalog_name}/game-entries
    - 45 ms
- PUT /users/{user_id}/catalogs/{catalog_name}/game-entries/{entry_title}
    - 24 ms
- DELETE /users/{user_id}/catalogs/{catalog_name}/game-entries/{entry_title}
    -28 ms

### movies
- GET /movies
    - 13 ms

### movie_entries
- GET /users/{user_id}/catalogs/{catalog_name}/movie-entries
    - 
- POST /users/{user_id}/catalogs/{catalog_name}/movie-entries
    - 18 ms
- PUT /users/{user_id}/catalogs/{catalog_name}/movie-entries/{entry_title}
    - 18 ms
- DELETE /users/{user_id}/catalogs/{catalog_name}/movie-entries/{entry_title}
    - 20 ms
### books
- GET /books
    - 17 ms

### book_entries
- GET /users/{user_id}/catalogs/{catalog_name}/book-entries
    -
- POST /users/{user_id}/catalogs/{catalog_name}/book-entries
    - 18 ms
- PUT /users/{user_id}/catalogs/{catalog_name}/book-entries/{entry_title}
    - 22 ms
- DELETE /users/{user_id}/catalogs/{catalog_name}/book-entries/{entry_title}
    - 17 ms

### other_entries
- GET /users/{user_id}/catalogs/{catalog_name}/other-entries
    -
- POST /users/{user_id}/catalogs/{catalog_name}/other-entries
    - 11 ms
- PUT /users/{user_id}/catalogs/{catalog_name}/other-entries/{entry_title}
    - 16 ms 
- DELETE /users/{user_id}/catalogs/{catalog_name}/other-entries/{entry_title}
    - 16 ms

## Top 3 Slowest & Improvements:
## 1. 

## 2.

## 3. 