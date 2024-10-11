
## Still needs:
- searching friends recommendations.
- liking and disliking.
- creating users.

# LOGGING IN/OUt
## '/user/login' (POST) (pass username and password)

Pass in a name and password to log that user in. Unrestricts read access to private records on that user's account and enables write access.

**Request**

'''json
{
  "name": "String"
  "password": "String"
}
'''

## '/user/logout' (POST)


# NAVIGATION
  - Locations
  - Self/follows -> catalog -> entries 
  - {userName} -> {catalogName} -> {entryTitle}

##'/location/back' (POST)
## '/location/current' (GET)
## '/location/listpossibiities' (GET)
## '/location/listpossibilities/condition' (GET)
## '/location/next' (POST)
## '/location/create' (POST)
## '/location/delete' (POST)

# FOLLOWING
## '/social/follow' (POST)
## '/social/following (GET)
## '/social/unfollow' (POST)
## '/social/list_people' (GET)

## '/social/search/{user}/{catalog}/recommendations' (GET)
## '/social/search/{title} (GET)
