import sqlalchemy
import os
import dotenv
from faker import Faker
import numpy as np
import random

def database_connection_url():
    dotenv.load_dotenv()
    return os.environ.get("POSTGRES_URI")

engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

with engine.begin() as connection:
    # Selects all users and their follower count, in case we want to use that as a scale for posts
    users = connection.execute(sqlalchemy.text(
        """
        with top_users as (
            select distinct
            following_id as user_id,
            count(*) over (partition by following_id) as followers
            from
            social
        ),
            users_with_no_followers as (
            select users.id as user_id, 0 as followers
            from users
            where users.id not in (select user_id from top_users)
        )

        select * from top_users
        join users on users.id = user_id
        union 
        select * from users_with_no_followers
        join users on users.id = user_id
        """
    )).all()
    

    print("Generating user->post mapping...")
    # Assuming normal distribution of posts, could also be negative binomial
    post_distribution = np.random.normal(275, 55, len(users))
    total_posts = 0
    user_post_mapping = []
    for (i, user) in enumerate(users):
        user_id = user.user_id
        name = user.name
        post_count = int(post_distribution[i])
        total_posts += post_count

        user_post_mapping.append(
            {
                "user_id": user_id,
                "name": name,
                "num_posts": post_count
            }
        )
    print("user->post mapping complete")
    print(f"total posts: {total_posts}\n")


    print("Generating post data for each user...")
    faker = Faker()
    catalog_types = ['games', 'books', 'movies', 'other']
    count = 0
    
    # Store games, movies, and book id's for faster sampling
    games = connection.execute(sqlalchemy.text("select id from games")).fetchall()
    games = [game[0] for game in games]
    movies = connection.execute(sqlalchemy.text("select id from movies")).fetchall()
    movies = [movie[0] for movie in movies]
    books = connection.execute(sqlalchemy.text("select id from books")).fetchall()
    books = [book[0] for book in books]

    for user in user_post_mapping:
        count+=1
        if count % 10 == 0: print(count)
        user_id = user['user_id']
        name = user['name']
        post_count = user['num_posts']

        catalogs = random.sample(catalog_types, random.randint(1,4))
        num_posts_each = int(post_count)//len(catalogs)
        
        for entry_type in catalogs:
            catalog_name = faker.user_name()
            private_catalog = faker.boolean()

            if (entry_type == 'games'):
                # Create a catalog with type games
                catalog = connection.execute(sqlalchemy.text(
                    f"""
                    insert into catalogs (user_id, name, type, private)
                    values ({user_id}, '{name}''s Games', 'games', {private_catalog})
                    returning id
                    """
                )).first()
                random_games = random.sample(games, num_posts_each)
                
                for game in random_games:
                    hours_played = random.randint(1, 5000)
                    opinion = faker.text(max_nb_chars=50)
                    rating = round(random.uniform(0, 10),2)
                    play_again = faker.boolean()
                    recommend = faker.boolean()

                    entry = connection.execute(sqlalchemy.text(
                        f"""
                        insert into entries (catalog_id, private, recommend)
                        values ({catalog.id}, {private_catalog}, {recommend}) returning id
                        """
                    )).first()

                    connection.execute(sqlalchemy.text(
                        f"""
                        insert into game_entry (entry_id, game_id, hours_played, opinion, rating, play_again)
                        values ({entry.id}, {game}, {hours_played}, '{opinion}', {rating}, {play_again})
                        """
                    ))
            if (entry_type == 'movies'):
                # Create a catalog with type games
                catalog = connection.execute(sqlalchemy.text(
                    f"""
                    insert into catalogs (user_id, name, type, private)
                    values ({user_id}, '{name}''s Movies', 'movies', {private_catalog})
                    returning id
                    """
                )).first()
                random_movies = random.sample(movies, num_posts_each)
                
                for movie in random_movies:
                    date_seen = faker.date_this_decade()
                    opinion = faker.text(max_nb_chars=50)
                    rating = round(random.uniform(0, 10),2)
                    watch_again = faker.boolean()
                    recommend = faker.boolean()

                    entry = connection.execute(sqlalchemy.text(
                        f"""
                        insert into entries (catalog_id, private, recommend)
                        values ({catalog.id}, {private_catalog}, {recommend}) returning id
                        """
                    )).first()

                    connection.execute(sqlalchemy.text(
                        f"""
                        insert into movie_entry (entry_id, movie_id, date_seen, opinion, rating, watch_again)
                        values ({entry.id}, {movie}, CAST('{date_seen}' AS DATE), '{opinion}', {rating}, {watch_again})
                        """
                    ))
            if (entry_type == 'books'):
                # Create a catalog with type games
                catalog = connection.execute(sqlalchemy.text(
                    f"""
                    insert into catalogs (user_id, name, type, private)
                    values ({user_id}, '{name}''s Books', 'books', {private_catalog})
                    returning id
                    """
                )).first()
                random_books = random.sample(books, num_posts_each)
                
                for book in random_books:
                    date_read = faker.date_this_decade()
                    opinion = faker.text(max_nb_chars=50)
                    rating = round(random.uniform(0, 10),2)
                    read_again = faker.boolean()
                    recommend = faker.boolean()

                    entry = connection.execute(sqlalchemy.text(
                        f"""
                        insert into entries (catalog_id, private, recommend)
                        values ({catalog.id}, {private_catalog}, {recommend}) returning id
                        """
                    )).first()

                    connection.execute(sqlalchemy.text(
                        f"""
                        insert into book_entry (entry_id, book_id, date_read, opinion, rating, read_again)
                        values ({entry.id}, {book}, CAST('{date_read}' AS DATE), '{opinion}', {rating}, {read_again})
                        """
                    ))
            if (entry_type == 'other'):
                # Create a catalog with type games
                catalog = connection.execute(sqlalchemy.text(
                    f"""
                    insert into catalogs (user_id, name, type, private)
                    values ({user_id}, '{name}''s Other Things', 'other', {private_catalog})
                    returning id
                    """
                )).first()
                random_things = faker.text(max_nb_chars=20)
                
                for other in random_things:
                    description = faker.text(max_nb_chars=50)
                    price = round(random.uniform(0,1000),2)
                    quality = faker.text(max_nb_chars=10)
                    date_obtained = faker.date_this_decade()
                    recommend = faker.boolean()

                    entry = connection.execute(sqlalchemy.text(
                        f"""
                        insert into entries (catalog_id, private, recommend)
                        values ({catalog.id}, {private_catalog}, {recommend}) returning id
                        """
                    )).first()

                    connection.execute(sqlalchemy.text(
                        f"""
                        insert into other_entry (entry_id, title, description, price, quality, date_obtained)
                        values ({entry.id}, '{other}', '{description}', '{price}', '{quality}', CAST('{date_obtained}' AS DATE))
                        """
                    ))
                    
    print("Post data generated.")
        



