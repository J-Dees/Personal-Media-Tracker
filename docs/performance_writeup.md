## NOTES:

# Performance write up:
### Entry generation script:
### Explanation:
- See fake_data folder for both scripts used to generate data.
- 1. `createUsers` generates 2000 users. It assigns a number of followers for each user based off a negative binomial distribution.
- 2. `createPosts` uses a normal distribution to assign numbers of posts for each user. Randomly assigns catalog types and even distributes post among those catalogs.

## Endpoint Performance:
- **Note: these numbers are rough averages.**
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
    - 56 ms
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
    - 57 ms
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
    - 54 ms
- POST /users/{user_id}/catalogs/{catalog_name}/book-entries
    - 18 ms
- PUT /users/{user_id}/catalogs/{catalog_name}/book-entries/{entry_title}
    - 22 ms
- DELETE /users/{user_id}/catalogs/{catalog_name}/book-entries/{entry_title}
    - 17 ms

### other_entries
- GET /users/{user_id}/catalogs/{catalog_name}/other-entries
    - 57 ms
- POST /users/{user_id}/catalogs/{catalog_name}/other-entries
    - 11 ms
- PUT /users/{user_id}/catalogs/{catalog_name}/other-entries/{entry_title}
    - 16 ms 
- DELETE /users/{user_id}/catalogs/{catalog_name}/other-entries/{entry_title}
    - 16 ms

## Top 3 Slowest & Improvements:
## 1. GET /users/{user_id}/followees/follow-recommendations
- Added indices on social.user_id and social.following_id. 
- This reduced the time from 137 ms to around 110 ms.

## 2. GET /users/{user_id}/followees/entries
- Added indices on all `catalogs.user_id` and `entries.catalog_id`.

`create index catalog_user_id_idx on catalogs (user_id)`

`create index entries_catalog_id_idx on entries (catalog_id)`
- This reduced the time from 131 ms to around 45 ms.


## 3.   GET /users/{user_id}/catalogs/{catalog_name}/movie-entries
- Note: this also includes game-entries, book-entries, and other-entries
- Adding the previous indices reduced the time from around 55 ms to around 8 ms.