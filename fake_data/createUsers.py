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

# Generate 2000 unique users with id, name, follower_count
num_users = 2_000
users = []
follower_mapping = []

popularity_sample_distribution = []
while len(popularity_sample_distribution) < num_users:
    samples = np.random.negative_binomial(0.2, 0.0006, num_users)
    popularity_sample_distribution = np.concatenate((popularity_sample_distribution, samples[samples < num_users]))


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

base_size = num_users // 20
remainder = num_users % 20

sizes = [base_size + (1 if i < remainder else 0) for i in range(20)]
ranges = [(sum(sizes[:i]), sum(sizes[:i+1])- (1 if i < 19 else 0)) for i in range(20)]

follower_count_range = {range : 0 for range in ranges}

for user in users:
    follower_count = user["follower_count"]

    for range in follower_count_range:
        if range[0] <= follower_count <= range[1]:
            follower_count_range[range] += 1

for range in follower_count_range:
    print(f"{range}: {follower_count_range[range]} ")

total_rows = len(users)
total_rows += sum(user["follower_count"] for user in users)

print(f"Total rows: {total_rows}")
print(f"Max follower count: {max(user['follower_count'] for user in users)}")
print()

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
                    social (user_id, following_id)
                values
                    (:user_id, :following_id)
                """
            ), {
                "user_id": follower,
                "following_id": user["user_id"]
            })

print("Database filled.")

