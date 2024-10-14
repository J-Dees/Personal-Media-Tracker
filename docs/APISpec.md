# API Specificatoin

## Table of contents

### User Functions
- `/user/login` (GET)
- `user/{user_id}` (DELETE)
- `user/create` (POST)

### Entries
- `user/{user_id}/catalogs/{catalog_name}/entries` (POST)
- `user/{user_id}/catalogs/{catalog_name}/entries/search` (GET)
- `user/{user_id}/catalog/{catalog_name}/entries/{entry_title}` (PUT)
- `user/{user_id}/catalogs/{catalog_name}/entries/{entry_title}` (DELETE)

### Catalogs
- `user/{user_id}/catalog` (POST) creating catalog
- `user/{user_id}/catalog/search` (GET) searching
- `user/{user_id}/catalog/{catalog_name}` (DELETE) delete catalog
- `user/{user_id}/catalog/{catalog_name}` (PUT)

### Following
- `user/{user_id}/social` (POST) follow a user.
- `user/{user_id}/social/search` (GET) get list of following
- `user/{user_id}/social/{follower_id}` (DELETE) delete a follow
- `user/{user_id}/social/{follower_id}/catalogs` (GET) return all catalogs
- `user/{user_id}/social/{follower_id}/catalogs/{catalog}/recommendations` (GET) list all recommendations from a catalog.
- `user/{user_id}/social/search/{title}` (GET) get all followers' entries with that title.

# User Functions
### `/user/login` (GET)

Pass in a username and responds with the user_id. When making calls with a user_id it un-restricts all private catalogs and entries. Also allows for appending and deleting catalogs and entries.

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

### `user/{user_id}/delete` (DELETE)

Delete user_id's account and all information related to it. Gives a confirmation or warning.

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
  "title" : "string",
  "opinion" : "string",
  "rating/10" : "float",
  "watch_again" : "boolean",
  "date_seen" : “String", user enters date in the formate yyyy-mm-dd
  “recommend” : “boolean”,
  "private" : “boolean",
  "last_modified": "now()" // use the current date
}
```

***Response***

```json
{
  "status":"string"
}
```

###`user/{user_id}/catalogs/{catalog_name}/entries/{entry_title}` (PUT)

Updates a specific catalog entry with any of the fields (optional) that are to be updated. The last modified attribute will be updated to the current time for each usage of the PUT request.

```json
{
  "title" : "string",
  "opinion" : "string",
  "rating/10" : "float",
  "watch_again" : "boolean",
  "date_seen" : “String", user enters date in the formate yyyy-mm-dd
  “recommend” : “boolean”,
  "private" : “boolean",
  "last_modified": "now()" // use the current date
}
```

### `user/{user_id}/catalogs/{catalog_name}/entries/search` (GET)

Gets a list of both public and private entries in catalog_name under user_id. The list will have 50 entries per page. Search is sorted based on the query parameter.

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

Get the next page of results.

### `user/{user_id}/catalogs/{catalog_name}/entries/{entry_title}` (DELETE) 

Deletes the entry under user_id in catalog_name with entry_title.

***Response***

```json
{
  “confirmation”: “string”
}
```

## Catalogs

### `user/{user_id}/catalogs/` (POST)

Creates a catalog for user_id. The request body has all the fields to be filled in for the catalog.

***Request***

```json
{
  "title" : "string",
  "type" : "string"
}
```

***Response***

```json
{
  "status":"string"
}
```

### `user/{user_id}/catalog/search` (GET)

Searches through a user’s catalogs using (optional) specified queries.

Parameters:
`title`: The title of a specific catalog
`type`: The type of catalog 
`page`: A specific page of catalogs in the query
`sort-col`: A column to sort the results by (either `title` or `type`)
`sort-order`: The order in which to display the results (`asc` or `desc`, default: `desc`)

Response:

A JSON response is produced with the following information:
`results`: An array of JSON objects representing the catalogs returned by the query
The catalogs will be listed by `title` and `type`
`previous`: The results contained in the previous page of catalogs, will return an empty array if no such page exists
`next`: The results contained in the next page of catalogs, will return an empty array if no such page exists

### `user/{user_id}/catalog/{catalog_name}` (DELETE)

Deletes the specified catalog `{catalog_name}` from a user’s lists of catalogs.

Response:

```json
{
	“status”: “string”
}
```

###  `user/{user_id}/catalog/{catalog_name}` (PUT)

Used to update the catalog_name

***Request***

```json
{
  “new_name”: “string”
}
```

***Response***
```json
{
  “confirmation”:”string”
}

# Following

### `user/{user_id}/social` (POST) 

follow a user

***Request***

```json
{
 “follower_id”: “string”
}
```

***Response***

```json
{
  “success”: “string”
}
```

### `user/{user_id}/social/search` (GET) 
Gets a list of all users user_id is following. The list will have 50 entries per page.

***Query Parameters***

- `search_page` (optional): The page number of the result.
- `sort_col` (default) is to sort by name alphabetically.

***Response***

JSON object of the following:

- `previous`: String
- `next`: String
- `results`: Array of names.
   - name strings.

### `user/{user_id}/social/{follower_id}` (DELETE) 

delete a follow from user_id

***Request***

```json
{
  “follower_id”: “string”
}
```

***Response***

```json
{
  “success”:”boolean”
}
```


### `user/{user_id}/social/{follower_id}/catalogs` (GET)

returns all catalogs

***Response***

```json
{
  “catalogs”: []
}
```

### `user/{user_id}/social/{follower_id}/catalogs/{catalog}/recommendations` (GET)

returns all entries in a catalog where recommend is true

***Response***

```json
{
  “Entry”: []
}
```

### `/{user_id}/social/search/{title}` (GET)

***Response***
```json
{
  “title” : [ ]
}
```
