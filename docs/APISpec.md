
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

### `/user/logout` (POST)
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

### `/location/back` (POST)
### `/location/current` (GET)
### `/location/listpossibiities` (GET)
### `/location/listpossibilities/condition` (GET)
### `/location/next` (POST)
### `/location/create` (POST)
### `/location/delete` (POST)

# FOLLOWING
## '/social/follow' (POST)
## '/social/following (GET)
## '/social/unfollow' (POST)
## '/social/list_people' (GET)

## '/social/search/{user}/{catalog}/recommendations' (GET)
## '/social/search/{title} (GET)
