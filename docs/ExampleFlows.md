## Example Flows
1. Paul, an avid Pokemon card collecter, logs in to the personal media tracker to create a new catalog of his entire Pokemon collection. Paul logins into his account using `POST /user/login` and successfully enters his username to login, he then calls `POST /users/{user_id}/catalog` to create a new catalog for his Pokemon cards. Paul finally uses `POST users/{user_id}/catalog/{catalog_id}/entries` for every card in his collection to add it to his media tracker. Paul knows several other Pokemon collectors using the personal media tracker, Paul calls `POST /users/{user_id}/social` and passes in the name of his friend Connor. Since Connor exists on the site, his user name is found and returned to Paul's follower list.
2. 2
3. 3
