
## Still needs:
- searching friends recommendations.
- liking and disliking.
- creating users.

# LOGGING IN/OUt
- POST /user/login (pass username and password)
- POST /user/logout

# NAVIGATION
- Locations
- - Self/follows -> catalog -> entries 

- POST /location/back
- GET /location/current
- GET /location/listpossibiities
- Get /location/listpossibilities/condition
- POST /location/next
- POST /location/create
- POST /location/delete

# FOLLOWING
- POST /social/manage/follow
- GET /social/manage/following
- POST /socail/manage/unfollow
- GET /social/manage/list_people
