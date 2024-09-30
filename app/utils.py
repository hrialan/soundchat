# utils.py

import os
import json
from datetime import datetime, timedelta
from flask import request, render_template, redirect
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import spotipy
import yaml

from app import app, db

if os.path.exists(".env"):
    load_dotenv()

# Load configuration
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

app_data = {
    "app_name": config["app_name"],
}

# Constants
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
SPOTIFY_EXPORT_EXPIRY_DAYS = 1

# TOKEN ENCRYPTION

cipher_suite = Fernet(ENCRYPTION_KEY)


def encrypt_token(token):
    token_str = json.dumps(token)
    return cipher_suite.encrypt(token_str.encode()).decode()


def decrypt_token(encrypted_token):
    token_str = (
        cipher_suite.decrypt(encrypted_token.encode()).decode().replace("'", '"')
    )
    return json.loads(token_str)


# FIRESTORE DATABASE

users_collection = db.collection("users")


def get_user_id():
    return request.cookies.get("spotify_user_id")


def get_user_data(user_id):
    try:
        user_doc = users_collection.document(user_id).get()
        if user_doc.exists:
            return user_doc.to_dict()
    except Exception as e:
        app.logger.error(f"Error getting user data: {e}")
    return {}


def set_user_data(user_id, data):
    try:
        users_collection.document(user_id).set(data)
    except Exception as e:
        app.logger.error(f"Error setting user data: {e}")


def is_export_expired(timestamp):
    if not timestamp:
        return True
    export_time = datetime.fromisoformat(timestamp)
    return datetime.now() - export_time > timedelta(days=SPOTIFY_EXPORT_EXPIRY_DAYS)


# SESSION / COOKIES


def add_session(user_data, session_id):
    new_session = {"session_id": session_id, "timestamp": datetime.now().isoformat()}
    if "sessions" not in user_data:
        user_data["sessions"] = []

    existing_session_index = next(
        (
            index
            for index, session in enumerate(user_data["sessions"])
            if session["session_id"] == session_id
        ),
        None,
    )

    if existing_session_index is not None:
        user_data["sessions"][existing_session_index]["timestamp"] = new_session[
            "timestamp"
        ]
    else:
        user_data["sessions"].append(new_session)

    # Keep only the 5 most recent sessions
    user_data["sessions"] = sorted(
        user_data["sessions"], key=lambda x: x["timestamp"], reverse=True
    )[:5]

    return user_data


def is_session_valid(user_data, session_id):
    if "sessions" not in user_data:
        return False
    return any(session["session_id"] == session_id for session in user_data["sessions"])


def get_token_from_cookie():
    user_id = get_user_id()
    if user_id:
        user_data = get_user_data(user_id)
        if user_data:
            encrypted_token_info = user_data.get("token_info")
            if encrypted_token_info and is_session_valid(
                user_data, request.cookies.get("session_id")
            ):
                return decrypt_token(encrypted_token_info)
    return None


# SPOTIFY AUTHENTICATION


def handle_spotify_auth(auth_manager, cache_handler):
    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        return redirect("/")

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        app.logger.info("User not connected, redirecting to Spotify login")
        auth_url = auth_manager.get_authorize_url()
        return render_template("index.html", app_data=app_data, auth_url=auth_url)

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    try:
        spotify.me()
    except spotipy.SpotifyException as e:
        if e.http_status == 403:
            app.logger.info("User not authorized")
            return render_template("unauthorized.html", app_data=app_data)

    app.logger.info("User connected: %s", spotify.me()["display_name"])

    user_id = spotify.me()["id"]
    username = spotify.me()["display_name"]

    return spotify, user_id, username
