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

fake = Faker()

# Generate 1000 unique users with id, name, follower_count
num_users = 10_000
users = []
follower_mapping = []

popularity_sample_distribution = np.random.default_rng().negative_binomial(0.3, 0.0006, num_users)

for i in range(1,num_users+1):
    users.append(
        {
            "id": i,
            "name": fake.unique.name(),
            "follower_count": int(popularity_sample_distribution[i-1])
        }
    )

print(f"{num_users} Unique Users Generated.\n")

print("Generating follower mapping...")
for user in users:
    num_followers = user["follower_count"]

    followers = random.sample(list(u["id"] for u in users), min(num_followers, num_users-1))

    if user["id"] in followers:
        followers.remove(user["id"])
    follower_mapping.append(
        {
            "user_id": user["id"],
            "followers": followers
        }
    )
print("Follower mapping generated.\n")

for user in users:
    user.pop("follower_count")

print(f"Begining to fill database with {num_users} users...")
with engine.begin() as connection:
    # Insert users
    connection.execute(sqlalchemy.text(
        """
        insert into
            users (id, name)
        values
            (:id, :name)
        """
    ), users)

    # Insert followers
    for user in follower_mapping:
        for follower in user["followers"]:
            connection.execute(sqlalchemy.text(
                """
                insert into
                    social (user_id, follower_id)
                values
                    (:user_id, :follower_id)
                """
            ), {
                "user_id": user["user_id"],
                "follower_id": follower
            })

print("Database filled.")