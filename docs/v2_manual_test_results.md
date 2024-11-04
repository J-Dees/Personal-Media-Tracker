# Example workflow 1
1. Paul, an avid Pokemon card collecter, logs in to the personal media tracker to create a new catalog of his entire Pokemon collection. Paul logins into his account using `GET /user/login` and successfully enters his username to login, he then calls `POST /users/{user_id}/catalog` to create a new catalog for his Pokemon cards. Paul finally uses `POST users/{user_id}/catalog/{catalog_id}/entries` for every card in his collection to add it to his media tracker. Paul knows several other Pokemon collectors using the personal media tracker, Paul calls `POST /users/{user_id}/social` and passes in the name of his friend Connor. Since Connor exists on the site, his user name is found and returned to Paul's follower list.

# Testing results
### GET /user/login:
#### CURL CALL:
       ```curl -X 'GET' \
  'http://127.0.0.1:8000/user/login?name=Paul' \
  -H 'accept: application/json'```
#### CURL RESPONSE:
      `Response Body: "OK"
      "GET /user/login?name=Paul HTTP/1.1" 200 OK`

### POST /users/{user_id}/catalog:
#### CURL CALL:
    `curl -X 'POST' \
  'http://127.0.0.1:8000/user/7/catalogs' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Paul'\''s Pokemon",
  "type": "other",
  "private": false
}'`
#### CURL RESPONSE:
    `Response Body: "OK"
    "POST /user/7/catalogs HTTP/1.1"
 201 Created`
    
### POST users/{user_id}/catalog/{catalog_id}/entries:
#### CURL CALL:
    `curl -X 'POST' \
  'http://127.0.0.1:8000/user/7/catalogs/Paul%27s%20Pokemon/other_entries' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Greninja ex 214/167",
  "description": "As long as this Pokémon is on your Bench, prevent all damage done to this Pokémon by attacks (both yours and your opponent'\''s).",
  "price": 305,
  "quality": "Special Illustration Rare",
  "date_obtained": "2024-10-09",
  "recommend": true,
  "private": false
}'`
#### CURL RESPONSE:
    `Response Body: "OK"
    "POST /user/7/catalogs/Paul%27s%20Pokemon/other_entries HTTP/1.1" 200 OK`

### POST users/{user_id}/catalog/{catalog_id}/entries:
#### CURL CALL:
    `curl -X 'POST' \
  'http://127.0.0.1:8000/user/7/catalogs/Paul%27s%20Pokemon/other_entries' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Mew ex 232/091",
  "description": "Shiny Mew",
  "price": 169,
  "quality": "Special Illustration Rare",
  "date_obtained": "2024-07-23",
  "recommend": true,
  "private": false
}'`
#### CURL RESPONSE:
    `Response Body: "OK"
    "POST /user/7/catalogs/Paul%27s%20Pokemon/other_entries HTTP/1.1" 200 OK`

### POST /users/{user_id}/social:
#### CURL CALL:
    `curl -X 'POST' \
  'http://127.0.0.1:8000/user/7/social?user_name=Connor' \
  -H 'accept: application/json' \
  -d ''`
#### CURL RESPONSE:
    `Response Body: "OK"
    "POST /user/7/social?user_name=Connor HTTP/1.1" 200 OK`

# Example workflow 2
2. On Saturday, Jonathan is hoping to relax after a busy week by watching a movie. He is unsure of what to watch, but he knows about the personal media tracker that his friends use to write opinions and recommendations for movies that they have seen. Jonathan creates an account for the personal media tracker by calling `POST /user/create` and immediately follows his friend Aiden by calling `POST  user/{user_id}/social` passing Aiden’s account name. Jonathan uses `GET user/{user_id}/social/{follower_id}/catalogs` to get and  browse a list of Aiden’s catalogs. Jonathan finds a public catalog titled “my_movies”. Finally, Jonathan calls  `GET user/{user_id}/social/{user_name}/catalogs/{catalog}/recommendations` on Aiden’s “my_movies” catalog to see the list of movie entries that Aiden personally recommends. Jonathan sees “Cars” on Aiden’s list along with a favorable rating and opinion and decides to watch that to end his chill Saturday evening.

# Testing results
### POST /user/create:
#### CURL CALL:
       ```curl -X 'POST' \
  'http://127.0.0.1:8000/user/create?name=Jonathan' \
  -H 'accept: application/json' \
  -d ''```
#### CURL RESPONSE:
      `Response Body: "OK"
      "POST /user/create?name=Jonathan HTTP/1.1" 201 Created`

### POST  user/{user_id}/social:
#### CURL CALL:
       ```curl -X 'POST' \
  'http://127.0.0.1:8000/user/8/social?user_name=Aiden' \
  -H 'accept: application/json' \
  -d ''```
#### CURL RESPONSE:
      `Response Body: "OK"
      "POST /user/8/social?user_name=Aiden HTTP/1.1" OK`

### GET user/{user_id}/social/{follower_id}/catalogs:
#### CURL CALL:
       ```curl -X 'GET' \
  'http://127.0.0.1:8000/user/8/social/Aiden/catalogs' \
  -H 'accept: application/json'```
#### CURL RESPONSE:
      `Response Body: [
  {
    "name": "my_movies",
    "type": "movies"
  }
]
      "GET /user/8/social/Aiden/catalogs HTTP/1.1" 200 OK`

### GET user/{user_id}/social/{user_name}/catalogs/{catalog}/recommendations:
#### CURL CALL:
       ```curl -X 'GET' \
  'http://127.0.0.1:8000/user/11/social/Aiden/catalogs/my_movies/recommendations' \
  -H 'accept: application/json'```
#### CURL RESPONSE:
      `Response Body: [
  {
    "movie_title": "Cars",
    "year": 2006,
    "date_seen": "2014-10-07",
    "opinion": "Lightning McQueen is cool",
    "rating": 9.3,
    "watch_again": true,
    "recommend": true
  }
]
      "GET /user/11/social/Aiden/catalogs/my_movies/recommendations HTTP/1.1" 200 OK