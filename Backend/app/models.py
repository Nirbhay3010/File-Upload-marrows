import bson, os
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

DATABASE_URL=os.environ.get('DATABASE_URL') or 'mongodb://localhost:27017/myDatabase'
client = MongoClient(DATABASE_URL)
db = client.myDatabase

class User:
    """User Model"""
    def __init__(self):
        return

    def create(self, email="", password=""):
        """Create a new user"""
        user = self.get_by_email(email)
        if user:
            return
        new_user = db.users.insert_one(
            {
                "email": email,
                "password": self.encrypt_password(password),
                "active": True
            }
        )
        print(new_user)
        return self.get_by_id(new_user.inserted_id)

    def get_all(self):
        """Get all users"""
        users = db.users.find({"active": True})
        return [{**user, "_id": str(user["_id"])} for user in users]

    def get_by_id(self, user_id):
        """Get a user by id"""
        user = db.users.find_one({"_id": bson.ObjectId(user_id), "active": True})
        if not user:
            return
        user["_id"] = str(user["_id"])
        user.pop("password")
        return user

    def get_by_email(self, email):
        """Get a user by email"""
        user = db.users.find_one({"email": email, "active": True})
        if not user:
            return
        user["_id"] = str(user["_id"])
        return user

    def update(self, user_id, name=""):
        """Update a user"""
        data = {}
        if name:
            data["name"] = name
        user = db.users.update_one(
            {"_id": bson.ObjectId(user_id)},
            {
                "$set": data
            }
        )
        user = self.get_by_id(user_id)
        return user

    def delete(self, user_id):
        """Delete a user"""
        user = db.users.delete_one({"_id": bson.ObjectId(user_id)})
        user = self.get_by_id(user_id)
        return user

    def disable_account(self, user_id):
        """Disable a user account"""
        user = db.users.update_one(
            {"_id": bson.ObjectId(user_id)},
            {"$set": {"active": False}}
        )
        user = self.get_by_id(user_id)
        return user

    def encrypt_password(self, password):
        """Encrypt password"""
        return generate_password_hash(password)

    def login(self, email, password):
        """Login a user"""
        user = self.get_by_email(email)
        if not user or not check_password_hash(user["password"], password):
            return
        user.pop("password")
        return user
    

class Movies:
    """Movies Model"""
    def __init__(self):
        return

    def create(self, title="", description="", image_url="", category="", user_id=""):
        """Create a new Movie"""
        movie = self.get_by_user_id_and_title(user_id, title)
        if movie:
            return
        new_movie = db.movies.insert_one(
            {
                "title": title,
                "categories": description,
                "duraction": image_url,
                "rating": category,
                "release_year": user_id,
            }
        )
        return self.get_by_id(new_movie.inserted_id)

    def get_by_id(self, movie_id):
        movie = db.movies.find_one({"_id": bson.ObjectId(movie_id)})
        if not movie:
            return
        movie["_id"] = str(movie["_id"])
        return movie

    def get_by_user_id(self, user_id):
        """Get all movies created by a user"""
        movies = db.movies.find({"user_id": user_id})
        return [{**movie, "_id": str(movie["_id"])} for movie in movies]

    def get_by_category(self, category):
        """Get all movies by category"""
        movies = db.movies.find({"category": category})
        return [movie for movie in movies]

    def get_by_user_id_and_category(self, user_id, category):
        """Get all movies by category for a particular user"""
        movies = db.movies.find({"user_id": user_id, "category": category})
        return [{**movie, "_id": str(movie["_id"])} for movie in movies]

    def get_by_user_id_and_title(self, user_id, title):
        """Get a movie given its title and author"""
        movie = db.movies.find_one({"user_id": user_id, "title": title})
        if not movie:
            return
        movie["_id"] = str(movie["_id"])
        return movie

