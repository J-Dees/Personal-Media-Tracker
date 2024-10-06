# User Stories and Exceptions
## User Stories
1. As an avid movie watcher, I want to know what movies my friends have seen so that I can discuss those movies with them.
2. As a person who is always looking for something to watch on a Saturday night, I want to get ratings and recommendations from people I know, so I can find a new movie to watch.
3. As somebody who has watched hundreds of movies, I would like to check if I've seen certain movies and my opinions on them, so I decide whether to rewatch the movie.
4. As a gamer, I don't want to waste money on games, so I would like to see my friend's opinions and recommendations on games before making a purchase.
5. As an avid video game completionist, I want to keep track of the many games I play and have played, so I can share them with friends and possibly find games to play online together.
6. As an avid reader, I want to track books I would like to read in the future, so I don't forget any suggestions from friends or family.
7. As a coffee cup collector, I want to manage a catalog of my collection, so that I can efficiently search for items already in my collection.
8. As a card collector and trader, I want to keep track of my card ratings and prices so I can effectively trade with others at conventions or online.
9. As a rare coin collector, I want to see the collections of others, so I can plan trades and see their opinions on coins.
10. As a collector of figurines, I would like to see other people’s collections and compare them to my own. That way I can view what they have and what I have to discuss trades.
11. As somebody who has been deceived by online reviews for movies, books, and games, I would like to see the opinions of people I trust, so I can make decisions on what to watch, read, or play.
12. As someone who loves interacting with friends, I like to give feedback to my friend's opinions on movies, books, and video games. So that I can see what we share in common or disagree on and talk about it with them.

## Possible Exceptions
1. If a user logs in with an incorrect username or password, then an error message will be shown.
2. If a user tries to create a catalog but can’t, then give them a specific error for why. This could be duplicate name or invalid catalog type
3. If a user tries to create an entry with a duplicate title, then have them re-enter a different title.
4. if a user tries to delete an entry that doesn’t exist, then let them know nothing was found and nothing was deleted.
5. if a user deletes an entry by accident, then always give them a confirmation to delete W/ entry description.
6. if a user searches for a user or catalog with an incorrect name, then give them an error specifying to check spelling.
7. if a user tries to remove a friend, then give an error specific to having no friends to remove or incorrect spelling.
8. If a user searches for a catalog or an entry but it is private, then a match will be made but don’t display anything or display that the entry or catalog is private.
9. If a user logs in but doesn’t have an account, then ask if they would like to create an account with the name and password provided also prompt a display name.
10. If a user does any search and there are no matches, then give feedback that there are no matches.
11. If a user enters a name in any field with forbidden characters, then handle the exception and prompt for a different name without forbidden characters. (may not be necessary depending on how we store/use titles other fields)
12. If a user tries to go back through the menu system too far then give an exception stating that they can’t go back further.

