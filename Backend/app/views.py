import jwt, os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from .validator import validate_email_and_password, validate_user
from .models import db,User
from .auth_middleware import token_required
from flask_cors import CORS, cross_origin
import json
import pandas as pd
from bson import json_util
import threading
from datetime import datetime

load_dotenv()

progress_lock = threading.Lock()
CHUNK_SIZE = 1000

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route("/hello",methods=["GET"])
def hello():
    return "Hellooo"

@app.route("/users/signup", methods=["POST"])
def add_user():
    try:
        user = json.loads(request.data)
        if not user:
            return {
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }, 400
        is_validated = validate_user(**user)
        if is_validated is not True:
            return dict(message='Invalid data', data=None, error=is_validated), 400
        user = User().create(**user)
        if not user:
            return {
                "message": "User already exists",
                "error": "Conflict",
                "data": None
            }, 409
        return {
            "message": "Successfully created new user",
            "data": user
        }, 201
    except Exception as e:
        print(e)
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500

@app.route("/users/login", methods=["POST"])
def login():
    try:
        
        data = json.loads(request.data)
        print(data)
        if not data:
            return {
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }, 400
        # validate input
        is_validated = validate_email_and_password(data.get('email'), data.get('password'))
        print(is_validated)
        if is_validated is not True:
            return dict(message='Invalid data', data=None, error=is_validated), 400
        user = User().login(
            data["email"],
            data["password"]
        )
        if user:
            try:
                # token should expire after 24 hrs
                user["token"] = jwt.encode(
                    {"user_id": user["_id"]},
                    app.config["SECRET_KEY"],
                    algorithm="HS256"
                )
                return {
                    "message": "Successfully fetched auth token",
                    "data": user
                }
            except Exception as e:
                return {
                    "error": "Something went wrong",
                    "message": str(e)
                }, 500
        return {
            "message": "Error fetching auth token!, invalid email or password",
            "data": None,
            "error": "Unauthorized"
        }, 404
    except Exception as e:
        return {
                "message": "Something went wrong!",
                "error": str(e),
                "data": None
        }, 500


@app.route("/users/", methods=["GET"])
@token_required
def get_current_user(current_user):
    return jsonify({
        "message": "successfully retrieved user profile",
        "data": current_user
    })

@app.route("/users/", methods=["PUT"])
@token_required
def update_user(current_user):
    try:
        user = request.json
        if user.get("name"):
            user = User().update(current_user["_id"], user["name"])
            return jsonify({
                "message": "successfully updated account",
                "data": user
            }), 201
        return {
            "message": "Invalid data, you can only update your account name!",
            "data": None,
            "error": "Bad Request"
        }, 400
    except Exception as e:
        return jsonify({
            "message": "failed to update account",
            "error": str(e),
            "data": None
        }), 400


@app.route('/api/movies', methods=["GET"])
@token_required
def get_movies_api(user):
    page = int(request.args.get('page', 1))
    sort_by = request.args.get('sort_by')
    page_size = int(request.args.get('pageSize'))
    user_id = user["_id"]
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    query = {"user_id":user_id}
    movies = get_movies(page_size, page, sort_by, query)
    for doc in movies:
        doc['date_added'] = doc['date_added'].strftime('%Y-%m-%d %H:%M:%S')
        doc['createdAt'] = doc['createdAt'].strftime('%Y-%m-%d %H:%M:%S')
    return json.loads(json_util.dumps(movies))


# @app.errorhandler(404)
# def forbidden(e):
#     return jsonify({
#         "message": "Endpoint Not Found",
#         "error": str(e),
#         "data": None
#     }), 404

def get_movies(page_size, page=1, sort_by=None, query={}):
    collection = db.movies
    skip = (page - 1) * page_size

    if sort_by:
        movies = collection.find(query).sort(sort_by, 1)
    else:
        movies = collection.find(query).skip(skip).limit(page_size)
    
    return list(movies)
    
def get_user_id_from_token(token):
    try:
        decoded_token = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
        user_id = decoded_token['user_id']
    except Exception:
        return None
    return user_id

@app.route("/upload_movies/", methods=["POST"])
@token_required
def upload_movie(user):
    print(request)
    print(request.files)
    print(request.form)
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    print(user)
    user_id = user.get("_id")
    if file:
    
        with progress_lock:
            if user_id not in upload_progress:
                upload_progress[user_id] = 0

        # Initialize chunk counter
        chunk_counter = 0

        # Process file in chunks
        for chunk in pd.read_csv(file, chunksize=CHUNK_SIZE):
            
            print("jkabfjf")
            process_chunk(chunk, user_id)
            chunk_counter += 1

        return 'CSV data uploaded successfully'


@app.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Forbidden",
        "error": str(e),
        "data": None
    }), 403


upload_progress = {}

def process_chunk(chunk, user_id):
    global upload_progress
    # Convert chunk to MongoDB documents
    documents = chunk.to_dict(orient='records')
    # Add user_id field to each document
    for doc in documents:
        
        doc['date_added'] = datetime.strptime(doc['date_added'], '%B %d, %Y')
        # Add createdAt field with default value
        doc['createdAt'] = datetime.utcnow()
        doc['user_id'] = user_id
        for key, value in doc.items():
            if value is None or pd.isna(value):
                doc[key] = None
    # Insert documents into MongoDB collection
    db.movies.insert_many(documents)
    print(documents)
    # collection.insert_many(documents)
    upload_progress[user_id] += len(documents)