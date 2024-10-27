# Example workflow
3. Connor hears about a new personal media tracker and wants to use it to keep track of the video games he has played.
   He creates an account by calling `POST /user/create`. Connor logs in calling `GET /user/login`. After that, he creates a
   catalog for his games by calling `POST user/{user_id}/catalog` and passing in the title “my_games” and the catalog type of “Game”. He then creates
   an entry using `POST user/{user_id}/catalogs/{catalog_name}/entries`. He creates an entry for “Omori” with a rating of 8/10, he played for 200 hours.
   After creating the entry, he thinks to himself that “Omori” is actually the greatest psychological horror game and wants
   to change his rating. He calls `PUT /user/{user_id}/catalogs/{catalog_name}/entries/{entry_title}` and passes a new rating of 10/10.

# Testing results
### POST /user/create:
CURL CALL:
       `curl -X 'POST' \
      'http://127.0.0.1:8000/user_functionsuser/create?name=Connor' \
      -H 'accept: application/json' \
      -d ''`
CURL RESPONSE:
      `Response Body: "OK"
      "POST /user/create?name=Connor HTTP/1.1" 201 Created`

### GET /user/login:
CURL CALL:
      `curl -X 'GET' \
      'http://127.0.0.1:8000/user_functionsuser/login?name=Connor' \
      -H 'accept: application/json'`
CURL RESPONSE:
      `Response Body: 
      {
        "user_id": 14
      }
      "GET /user/login?name=Connor HTTP/1.1" 200 OK`

### GET /user/{user_id}/catalogs:
CURL CALL:
    `curl -X 'POST' \
    'http://127.0.0.1:8000/catalogsuser/14/catalogs' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "name": "my_games",
    "type": "games",
    "private": false`
CURL RESPONSE:
    `Response Body: "OK"
    "POST /user/14/catalogs HTTP/1.1" 201 CREATED`

### /user/{user_id}/catalogs/{catalog_name}/game_entries
CURL CALL:
    `curl -X 'POST' \
    'http://127.0.0.1:8000/entriesuser/14/catalogs/%7Bcatalog_name%7D/game_entries?catalog_id=5' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "title": "Omori",
    "opinion": "This game is great",
    "rating": 8,
    "hours_played": 200,
    "play_again": true,
    "recommend": true,
    "private": true`
CURL RESPONSE:
    `Response Body: "OK"
    "POST /user/14/catalogs/%7Bcatalog_name%7D/game_entries?catalog_id=5 HTTP/1.1" 201 Created`
    
### /user/{user_id}/catalogs/{catalog_name}/entries/game_entries
CURL CALL:
    `curl -X 'PUT' \
    'http://127.0.0.1:8000/entriesuser/14/catalogs/my_games/entries/Omori' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "opinion": "This is the best game ever made!",
    "rating": 10.0,
    "hours_played": 2500,
    "play_again": true
    }'`
CURL RESPONSE:
    `Response Body: "OK"
    "PUT /user/14/catalogs/my_games/entries/Omori HTTP/1.1" 200 OK`


    

