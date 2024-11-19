## Case 1: Read Skew -***maybe***- Non Repeatable Read
**T1**: ```GET /users/{user_id}/catalogs?page=2&order_by=name&direction=asc``` \
**T2**: ```DELETE /users/{user_id}/catalogs/{catalog_id}```\
![image](concurrency_1.png)
### Solution:
- Using a repeatable read isolation level will allow T1 to read twice and get consistent results. Thus T1 will have no knowlage of the delete.

## Case 2:
- 

## Case 3:
