# API Specificatoin

## Table of contents
### User Functions
- `/user/login` (GET)
- `user/{user_id}/delete` (DELETE)
- `user/create` (POST)
- `user/{user_id}/catalogs/{catalog_name}/entries/` (GET) 

### Entries
- `user/{user_id}/catalogs/{catalog_name}/entries` (POST)
- `user/{user_id}/catalog/{catalog_name}/entries/?page=<token>` (GET) 

### Catalogs
- `user/{user_id}/catalog` (POST) 
- `user/{user_id}/catalog` (GET) 
- `user/{user_id}/catalog` (GET) 
- `user/{user_id}/catalog/{catalog_name}` (DELETE) 

- `/{user_id}/{catalogName}/?page=<token>` (GET)
- `/{user_id}/catalog/listpossibiities` (GET)
- `/{user_id}/location/listpossibilities/condition` (GET)
- `/{user_id}/location/next` (POST)
- `/{user_id}/location` (POST)
- `/{user_id}/location/{location_id}` (DELETE)

### Following
- `user/{user_id}/social` (POST) 
- `user/{user_id}/social` (GET) 
- `user/{user_id}/social/{user_id}` (DELETE)

- `user/{user_id}/social/{user_id}` (GET) 

- `user/{user_id}/social/`
- `user/{user_id}/social/` (GET)

- `/{user_id}/social/{user_name}/search/{catalog}/recommendations` (GET)
- `/{user_id}/social/search/{title}` (GET)



# User Functions
### `/user/login` (GET)

Pass in a username and responds with the user_id. When making calls with a user_id it unrestricts all private catalogs and entries. Also allows for appending and deleting catalogs and entries. 

**Request**:

```json
{
  "name": "string"
}
```

**Response**
```json
{
  "user_id": "UUID"
}
```

#NO NEED FOR LOGOUT:
### `/user/{user_id}/logout` (POST)
Logs out the current user. Re-restricts access to private records and write accesss. Gives an error if no-one is logged in.
**Response**
```json
{
"success": "boolean"
}
```

# Creating and Deteling Users

### `user/{user_id}/delete` (DELETE)

Delete user_id's account and all information related to it. Give confirmation warning.

**Response**

```json
{
  "confirmation": "string"
}
```

### `user/create` (POST)

Create a new user account with the specified name. gives status feedback for successful or any errors.

***Request***

```json
{
  "username": "string"
}
```

***Response***

```json
{
  "status": "string",
  "user_id": "int"
}
```

# Entries

### `user/{user_id}/catalogs/{catalog_name}/entries` (POST)

Creates an entry for user_id in catalog_name. The request body has all the fields to be filled in for the entry.

***Request***

```json
{
  "title":"string",
  "opinion":"string",
  "rating/10":"float",
  "watch_again":"boolean",
  "date_seen":"String", user enters date in the formate yyyy-mm-dd
  "private":"boolean"
  "creation_date": "now()" use the current date
}
```

***Response***

```json
{
  "status":"string"
}
```

### `user/{user_id}/catalogs/{catalog_name}/entries/` (GET) list entries

Gets a list of both public and private entries in catalog_name under user_id. The list will have 50 entries per page. Search is sorted based on the querty parameter.

***Query Parameters***

- `title` (optional): Search for a specific title.
- `description` (optional): Search for descriptions containing a specific string.
- `search_page` (optional): The page number of the result.
- `sort_col` (optional) the column to sort results by. Possible values: `title`, `date_seen `, `rating/10`, (Default)`creation_date`.
- `sort_order` (optional) The sort order of result. Possible values: `asc`, (Default)`desc`

***Response***

JSON object of the following:

- `previous`: String
- `next`: String
- `results`: Array of objects either movies, books, games, or default.
   - attributes of the objects.

###`user/{user_id}/catalog/{catalog_name}/entries/?page=<token>` (GET) 

Gets the next page of results.

#CAN`user/{user_id}/catalogs/{catalog_name}/entries/` (GET) do this?
### `user/{user_id}/catalog/{catalog_name}/entries/search?select="name"` (GET) search with column "name"

### `user/{user_id}/catalogs/{catalog_name}/entries/{entry_title}` (DELETE) delete entry

Create an entry in catalog_name
**json**

##Catalogs

### `user/{user_id}/catalog` (POST) create catalog
### `user/{user_id}/catalog` (GET) list catalogs.
### `user/{user_id}/catalog` (GET) next page of results.
### `user/{user_id}/catalog/{catalog_name}` (DELETE) delete catalog


### `/{user_id}/{catalogName}/?page=<token>` (GET)
### `/{user_id}/catalog/listpossibiities` (GET)
### `/{user_id}/location/listpossibilities/condition` (GET)
### `/{user_id}/location/next` (POST)
### `/{user_id}/location` (POST)
### `/{user_id}/location/{location_id}` (DELETE)

# FOLLOWING
### `user/{user_id}/social` (POST) Follow a new person.
### `user/{user_id}/social` (GET) List who the user follows.
### `user/{user_id}/social/{user_id}` (DELETE) remove a follow 

### `user/{user_id}/social/{user_id} (GET) List the 


### `user/{user_id}/social/`
### `user/{user_id}/social/` (GET)

### `/{user_id}/social/{user_name}/search/{catalog}/recommendations` (GET)
### `/{user_id}/social/search/{title}` (GET)
