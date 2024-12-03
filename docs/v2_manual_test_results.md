# Example workflow 1
1. Paul, an avid Pokemon card collecter, logs in to the personal media tracker to create a new catalog of his entire Pokemon collection. Paul logins into his account using `GET /users/{user_name}` and successfully enters his username to login, he then calls `POST /users/{user_id}/catalogs` to create a new catalog for his Pokemon cards. Paul finally uses `POST users/{user_id}/catalog/{catalog_id}/entries` for every card in his collection to add it to his media tracker. Paul knows several other Pokemon collectors using the personal media tracker, Paul calls `POST /users/{user_id}/followees` and passes in the name of his friend Connor. Since Connor exists on the site, his user name is found and returned to Paul's follower list.

# Testing results
### GET /users/{user_name}:
#### CURL CALL:
```
curl -X 'GET' \
'http://127.0.0.1:8000/users/{user_name}?name=Paul' \
-H 'accept: application/json'
```
#### CURL RESPONSE:
```
Response Body: 
  {
    "user_id": 7
  }
"GET /user/login?name=Paul HTTP/1.1" 200 OK
```

### POST /users/{user_id}/catalogs:
#### CURL CALL:
```
  curl -X 'POST' \
'http://127.0.0.1:8000/user/7/catalogs' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{
"name": "Paul'\''s Pokemon",
"type": "other",
"private": false
}'
```
#### CURL RESPONSE:
```
Response Body: 
  {
    "Catalog with name Paul's Pokemon created"
  }
"POST /user/7/catalogs HTTP/1.1" 201 Created
 ```
    
### POST users/{user_id}/catalogs/{catalog_name}/other-entries:
#### CURL CALL:
```
curl -X 'POST' \
  'http://127.0.0.1:3000/users/7/catalogs/Paul%27s%20Pokemon/other-entries' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Greninja ex 214/167",
  "description": "As long as this Pokémon is on your Bench, prevent all damage done to this Pokémon by attacks (both yours and your opponent'\''s)."/,
  "price": 305,
  "quality": "Special Illustration Rare",
  "date_obtained": "2024-10-09",
  "recommend": true,
  "private": false
}'
```
#### CURL RESPONSE:
```
Response Body:
  {
    "response": other entry created."
  }
"POST /users/7/catalogs/Paul%27s%20Pokemon/other-entries HTTP/1.1" 201 Created
```

### POST users/{user_id}/catalogs/{catalog_name}/other-entries:
#### CURL CALL:
```
curl -X 'POST' \
  'http://127.0.0.1:3000/users/7/catalogs/Paul%27s%20Pokemon/other-entries' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Mew ex 232/091",
  "description": "Shiny Mew",
  "price": 169,
  "quality": "Special illustration Rare",
  "date_obtained": "2024-07-23",
  "recommend": true,
  "private": false
}'
```
#### CURL RESPONSE:
```
Response Body:
  {
    "response": "other entry created."
  }
"POST /user/7/catalogs/Paul%27s%20Pokemon/other_entries HTTP/1.1" 201 Created
```

### POST /users/{user_id}/followees:
#### CURL CALL:
```
curl -X 'POST' \
'http://127.0.0.1:8000/users/7/social/followees?user_name=Connor' \
-H 'accept: application/json' \
-d ''
```
#### CURL RESPONSE:
```
Response Body:
  {
    "response": "Following added"
  }
"POST /users/7/followees?user_name=Connor HTTP/1.1" 201 Created
```

# Example workflow 2
2. On Saturday, Jonathan is hoping to relax after a busy week by watching a movie. He is unsure of what to watch, but he knows about the personal media tracker that his friends use to write opinions and recommendations for movies that they have seen. Jonathan creates an account for the personal media tracker by calling `POST /user` and immediately follows his friend Aiden by calling `POST  user/{user_id}/followees` passing Aiden’s account name. Jonathan uses `GET users/{user_id}/followees/catalogs` to get and  browse a list of Aiden’s catalogs. Jonathan finds a public catalog titled “my_movies”. Finally, Jonathan calls  `GET users/{user_id}/followees/entries` on Aiden’s “my_movies” catalog to see the list of movie entries that Aiden personally recommends. Jonathan sees “Cars” on Aiden’s list along with a favorable rating and opinion and decides to watch that to end his chill Saturday evening.

# Testing results
### POST /users/:
#### CURL CALL:
```
curl -X 'POST' \
'http://127.0.0.1:8000/users?name=Jonathan' \
-H 'accept: application/json' \
-d ''
```
#### CURL RESPONSE:
```
Response Body:
  {
    "response": "User created"
  }
"POST /user?name=Jonathan HTTP/1.1" 201 Created
```

### POST  user/{user_id}/followees:
#### CURL CALL:
```
curl -X 'POST' \
'http://127.0.0.1:8000/user/8/followees?user_name=Aiden' \
-H 'accept: application/json' \
-d ''
```
#### CURL RESPONSE:
```
Response Body:
  {
    "response": "User created"
  }
"POST /user/8/social?user_name=Aiden HTTP/1.1" 201 Created
```

### GET user/{user_id}/followees/catalogs:
#### CURL CALL:
```
curl -X 'GET' \
'http://127.0.0.1:8000/users/11/followees/catalogs?name=Aiden&direction=asc&page=1' \
-H 'accept: application/json'
```
#### CURL RESPONSE:
  ```
  {
    "page": 1,
    "max_page": 1,
    "content": [
      {
        "user": "Aiden",
        "catalog_name": "my_movies",
        "type": "movies"
      }
    ]
  }
  "GET /users/11/followees/catalogs?name=Aiden&direction=asc&page=1 HTTP/1.1" 200 OK
  ```

### GET users/{user_id}/followees/entries:
#### CURL CALL:
```
curl -X 'GET' \
'http://127.0.0.1:3000/users/11/followees/entries?page=1&following_name=Aiden&catalog=my_movies&recommend=false&order_by=title&direction=asc&return_type=movies' \
-H 'accept: application/json'
```
#### CURL RESPONSE:
```
{
  "page": 1,
  "max_page": 1,
  "content": [
    {
      "name": "Aiden",
      "catalog": "my_movies",
      "movie_title": "Cars",
      "rating": 9.3,
      "date_seen": "2014-10-07",
      "watch_again": true,
      "opinion": "Lightning McQueen is cool"
    }
  ]
}
"GET /users/11/followees/entries?page=1&following_name=Aiden&catalog=my_movies&recommend=false&order_by=title&direction=asc&return_type=movies HTTP/1.1" 200 OK
```