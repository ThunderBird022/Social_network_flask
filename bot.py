import requests
import random
import json
import pandas as pd
import sqlite3

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

API_BASE_URL = "http://127.0.0.1:5000"

def create_user(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{API_BASE_URL}/signup", json=data)
    return response.json()

def create_post(token, content):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"content": content}
    response = requests.post(f"{API_BASE_URL}/post", headers=headers, json=data)
    return response.json()

def like_post(token, post_id):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"post_id": post_id}
    response = requests.post(f"{API_BASE_URL}/like_post", headers=headers, json=data)
    return response.json()

def login(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{API_BASE_URL}/login", json=data)
    return response.json().get("token")

def main():
    # Signup users
    users = [f"user{i}" for i in range(config["number_of_users"])]
    for user in users:
        create_user(user, "password123")

    # Users creates posts
    post_ids = []
    for user in users:
        token = login(user, "password123")
        num_posts = random.randint(1, config["max_posts_per_user"])
        for _ in range(num_posts):
            post = create_post(token, "Random post content")
            post_ids.append(post["post_id"])

    # Users randomly like posts
    for user in users:
        token = login(user, "password123")
        for _ in range(random.randint(1, config["max_likes_per_user"])):
            post_id = random.choice(post_ids)
            like_post(token, post_id)

def df_from_query(query, args=()):
    conn = sqlite3.connect('app.db')
    df = pd.read_sql_query(query, conn, params=args)
    conn.close()
    return df

def check_users():
    df = df_from_query('SELECT * FROM user')
    print("Users in the database:")
    print(df.to_string(index=False))

def check_posts():
    df = df_from_query('SELECT * FROM post')
    print("Posts in the database:")
    print(df.to_string(index=False))

def check_likes():
    df = df_from_query('SELECT * FROM post_like')
    print("Likes in the database:")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
    check_users()
    check_posts()
    check_likes()
