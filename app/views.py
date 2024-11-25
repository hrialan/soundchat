# views.py

import os
import uuid
from datetime import datetime
from flask import (
    redirect,
    render_template,
    request,
    send_from_directory,
    make_response,
    session,
    flash,
)
from dotenv import load_dotenv
import spotipy
import yaml

from app import app
from .utils import (
    get_user_id,
    get_user_data,
    set_user_data,
    is_export_expired,
    encrypt_token,
    add_session,
    get_token_from_cookie,
    handle_spotify_auth,
)
from .playlist_generator import PlaylistGenerator

# Load environment variables from .env file if it exists
if os.path.exists(".env"):
    load_dotenv()

# Load configuration
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

app_data = {
    "app_name": config["app_name"],
}

# Constants
SPOTIFY_SCOPES = "playlist-read-private,playlist-modify-private,user-top-read,user-library-read,user-follow-read,user-read-recently-played"
COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static"), "favicon.ico")


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"An error occurred: {e}")
    return render_template("error.html", app_data=app_data), 500


@app.route("/")
def index():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    token_info = get_token_from_cookie()
    if token_info:
        cache_handler.save_token_to_cache(token_info)

    auth_manager = spotipy.oauth2.SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=SPOTIFY_SCOPES,
        cache_handler=cache_handler,
        show_dialog=True,
    )

    result = handle_spotify_auth(auth_manager, cache_handler)
    if isinstance(result, tuple):
        spotify, user_id, username = result
    else:
        return result

    user_data = get_user_data(user_id)
    encrypted_token = encrypt_token(cache_handler.get_cached_token())
    if not user_data:
        app.logger.info("Registering user in Firestore")
        username = spotify.me()["display_name"]
        user_data = {
            "username": username,
            "playlist_count": 0,
            "sessions": [],
        }
    user_data["token_info"] = encrypted_token

    session_id = request.cookies.get("session_id")
    response = make_response(
        render_template(
            "generate-playlist.html",
            app_data=app_data,
            user_name=spotify.me()["display_name"],
        )
    )

    if not session_id:
        app.logger.info("Creating new session")
        session_id = str(uuid.uuid4())
        response.set_cookie(
            "session_id",
            session_id,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=COOKIE_MAX_AGE,
        )

    user_data = add_session(user_data, session_id)
    set_user_data(user_id, user_data)

    response.set_cookie(
        "spotify_user_id",
        user_id,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=COOKIE_MAX_AGE,
    )
    return response


@app.route("/cgu")
def cgu():
    return render_template("cgu.html", app_data=app_data)


@app.route("/signout")
def sign_out():
    session.pop("token_info", None)
    user_id = get_user_id()
    if user_id:
        user_data = get_user_data(user_id)
        if user_data:
            user_data.pop("user_spotify_export", None)
            user_data.pop("export_timestamp", None)
            user_data.pop("token_info", None)
            user_data.pop("sessions", None)
            set_user_data(user_id, user_data)
        else:
            flash("Error during sign out. Please try again.", "error")
    else:
        flash("You are not logged in.", "error")
    app.logger.info("User signed out")
    response = make_response(redirect("/"))
    response.delete_cookie("spotify_user_id")
    return response


@app.route("/generate-playlist", methods=["POST"])
def generate_playlist():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    token_info = get_token_from_cookie()
    if token_info:
        cache_handler.save_token_to_cache(token_info)

    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect("/")

    if request.method == "POST":
        app.logger.info("Playlist generation request")
        spotify = spotipy.Spotify(auth_manager=auth_manager)

        try:
            spotify.me()
        except spotipy.SpotifyException as e:
            if e.http_status == 403:
                app.logger.info("User not authorized")
                return render_template("unauthorized.html", app_data=app_data)

        user_id = get_user_id()
        if not user_id:
            return redirect("/")

        user_data = get_user_data(user_id)
        if not user_data:
            flash("Error retrieving user data.", "error")
            return redirect("/")

        user_context = request.form.get("user_context")
        app.logger.info("User context: %s", user_context)

        playlist_generator = PlaylistGenerator(auth_manager=auth_manager)

        if "user_spotify_export" not in user_data or is_export_expired(
            user_data.get("export_timestamp")
        ):
            app.logger.info("Generating user Spotify export")
            user_spotify_export = playlist_generator.get_user_spotify_export()
            user_data["user_spotify_export"] = user_spotify_export
            user_data["export_timestamp"] = datetime.now().isoformat()
        else:
            app.logger.info("Using cached user Spotify export")
            user_spotify_export = user_data["user_spotify_export"]

        try:
            playlist_name, playlist_description, generated_playlist_tracks = (
                playlist_generator.ask_playlist_generation(
                    user_context=user_context, user_spotify_export=user_spotify_export
                )
            )
        except Exception as e:
            app.logger.error(f"Error generating playlist: {e}")
            flash("Error generating playlist.", "error")
            return render_template("error.html", app_data=app_data)

        modify_default_playlist = request.form.get("modify_default_playlist") == "on"

        try:
            if modify_default_playlist:
                app.logger.info("Modifying default playlist")
                playlist_generator.modify_user_playlist(
                    app_data["app_name"],
                    f"{playlist_name} : {playlist_description}",
                    generated_playlist_tracks,
                )
            else:
                app.logger.info("Creating new playlist: %s", playlist_name)
                playlist_generator.create_user_playlist(
                    playlist_name, playlist_description, generated_playlist_tracks
                )
        except Exception as e:
            app.logger.error(f"Error creating/modifying playlist: {e}")
            flash("Error creating/modifying playlist.", "error")
            return redirect("/")

        app.logger.info("Playlist generated")

        user_data["playlist_count"] = user_data.get("playlist_count", 0) + 1
        app.logger.info("Playlist count: %s", user_data["playlist_count"])

        max_number_of_playlists = 5
        show_donation_link = user_data["playlist_count"] >= max_number_of_playlists
        app.logger.info("Show donation link: %s", show_donation_link)

        set_user_data(user_id, user_data)

        return render_template(
            "playlist-generated.html",
            app_data=app_data,
            playlist_name=playlist_name,
            show_donation_link=show_donation_link,
            max_number_of_playlists=max_number_of_playlists,
        )
