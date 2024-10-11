
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
  "password": "String"
}
```

**Response**
```json
{
  "success": "boolean"
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

# NAVIGATION
  - Locations
  - Self/follows -> catalog -> entries 
  - {userName} -> {catalogName} -> {entryTitle}

### `/{user_id}/location/back` (POST)
### `/{user_id}/location/current` (GET)
### `/{user_id}/location/listpossibiities` (GET)
### `/{user_id}/location/listpossibilities/condition` (GET)
### `/{user_id}/location/next` (POST)
### `/{user_id}/location/create` (POST)
### `/{user_id}/location/delete` (DELETE)

# FOLLOWING
## `/{user_id}/social/follow` (POST)
## `/{user_id}/social/following` (GET)
## `/{user_id}/social/unfollow` (DELETE)
## `/{user_id}/social/list_people` (GET)

## `/{user_id}/social/search/{user_name}/{catalog}/recommendations` (GET)
## `/{user_id}/social/search/{title}` (GET)
