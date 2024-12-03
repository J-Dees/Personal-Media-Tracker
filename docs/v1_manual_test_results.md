# Example workflow 3
3. Connor hears about a new personal media tracker and wants to use it to keep track of the video games he has played.
   He creates an account by calling `POST /users`. Connor logs in calling `GET /users/{user_name}`. After that, he creates a public
   catalog for his games by calling `POST users/{user_id}/catalogs` and passing in the title “my_games”, the catalog type of “games”, and then a private setting of "false". He then creates
   an entry using `POST users/{user_id}/catalogs/{catalog_name}/game-entries`. He creates a public entry for the 2020 hit “Omori” with a rating of 8.0/10.0, he played for 200 hours, Connor claims that "Omori" is "such and amazing game that everyone should play" and sets the "play_again" and "recommend" attributes to true. 
   After creating the entry and playing for 50 more hours, he thinks to himself that “Omori” is actually the greatest psychological horror game ever made and wants
   to change his rating. He calls `PUT /users/{user_id}/catalogs/{catalog_name}/game-entries/{entry_title}` and passes a new rating of 10.0/10.0.

# Testing results
### POST /users:
#### CURL CALL:
 ```
curl -X 'POST' \
  'http://127.0.0.1:8000/users?name=Connor' \
  -H 'accept: application/json' \
  -d ''
```
#### CURL RESPONSE:
```
Response Body: "OK"
"POST /users?name=Connor HTTP/1.1" 201 Created
```
### GET /users/{user_name}:
#### CURL CALL:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/users/Connor' \
  -H 'accept: application/json'
```
#### CURL RESPONSE:
```
Response Body: 
{
  "user_id": 6
}
"GET /users/Connor HTTP/1.1" 200 OK
```
### POST /users/{user_id}/catalogs:
#### CURL CALL:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/users/6/catalogs' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "my_games",
  "type": "games",
  "private": false
}'
```
#### CURL RESPONSE:
```
Response Body: "Catalog with name my_games created"
"POST /users/6/catalogs HTTP/1.1" 201 Created
```
### POST /users/{user_id}/catalogs/{catalog_name}/game-entries
#### CURL CALL:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/users/6/catalogs/my_games/game-entries' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Omori",
  "year": 2020,
  "opinion": "This is such and amazing game that everyone should play",
  "rating": 8.0,
  "hours_played": 200,
  "play_again": true,
  "recommend": true,
  "private": false
}'
```
#### CURL RESPONSE:
```
Response Body: "Entry successfully created for Omori in my_games"
"POST /users/6/catalogs/my_games/game-entries HTTP/1.1" 201 Created
```   
### PUT /users/{user_id}/catalogs/{catalog_name}/game-entries/Omori
#### CURL CALL:
```
curl -X 'PUT' \
  'http://127.0.0.1:8000/users/6/catalogs/my_games/game-entries/Omori' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "opinion": "This is such and amazing game that everyone should play",
  "rating": 10.0,
  "hours_played": 250,
  "play_again": true
}'
```
#### CURL RESPONSE:
```
Response Body: "Entry 'Omori' updated successfully"
"PUT /users/6/catalogs/my_games/game-entries/Omori HTTP/1.1" 202 Accepted
```


    

