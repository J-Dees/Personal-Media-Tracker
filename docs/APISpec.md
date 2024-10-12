
## Still needs:
- searching friends recommendations.
- liking and disliking.
- creating users.

# LOGGING IN/OUT
### `/user/login` (POST) (pass username and password)

Pass in a name and password to log that user in. Unrestricts read access to private records on that user's account and enables write access. Gives an error if a user is already logged in.

**Request**:

```json
{
  "name": "String"
}u
```

**Response**
```json
{
  "user_id": "UUID"
}
```

### `/user/{user_id}/logout` (POST)

Logs out the current user. Re-restricts access to private records and write accesss. Gives an error if no-one is logged in.

**Response**
```json
{
"success": "boolean"
}
```

# User creating and Deteling

### `user/{user_id}/delete` (DELETE)

Delete user_id's account and all information related to it. Give confirmation warning.

### `user/create` (POST)

Create a new user account with the specified name and password. gicve

# NAVIGATION

##Entries

### `user/{user_id}/catalogs/{catalog_name}/entries/` (POST) create entry
### `user/{user_id}/catalogs/{catalog_name}/entries/` (GET) list entries
### `user/{user_id}/catalog/{catalog_name}/entries/?page=<token> (GET) next page of results.
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
