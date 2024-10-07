# playlist_generator.py

import json
import os
from .prompts import get_prompt, get_system_context

import spotipy
from dotenv import load_dotenv
from openai import OpenAI

if os.path.exists(".env"):
    load_dotenv()


class PlaylistGenerator:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.spotipy = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_user_spotify_export(self):
        try:
            top_tracks_long_term = self.spotipy.current_user_top_tracks(
                limit=30, time_range="long_term"
            )
            liked_tracks = self.spotipy.current_user_saved_tracks(limit=30)
            followed_artists = self.spotipy.current_user_followed_artists(limit=30)
            recently_played = self.spotipy.current_user_recently_played(limit=30)
            top_artists = self.spotipy.current_user_top_artists(
                limit=30, time_range="long_term"
            )
        except spotipy.SpotifyException as e:
            print(f"Error fetching Spotify data: {e}")
            return None

        spotify_export = {
            "Top Listened tracks": [
                f"{track['name']} - {track['artists'][0]['name']}"
                for track in top_tracks_long_term["items"]
            ],
            "Liked tracks": [
                f"{track['track']['name']} - {track['track']['artists'][0]['name']}"
                for track in liked_tracks["items"]
            ],
            "Followed artists": [
                artist["name"] for artist in followed_artists["artists"]["items"]
            ],
            "Recently Played": [
                f"{track['track']['name']} - {track['track']['artists'][0]['name']}"
                for track in recently_played["items"]
            ],
            "Top Listened Artists": [artist["name"] for artist in top_artists["items"]],
            "Top Listened Genres": [],
        }

        listened_genres = {}
        for artist in followed_artists["artists"]["items"] + top_artists["items"]:
            for genre in artist["genres"]:
                listened_genres[genre] = listened_genres.get(genre, 0) + 1

        top_genres = sorted(listened_genres.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]
        spotify_export["Top Listened Genres"] = [genre for genre, count in top_genres]

        return json.dumps(spotify_export, indent=4)

    def ask_playlist_generation(
        self, user_context, user_spotify_export, model_type="openai"
    ):

        prompt = get_prompt(user_context, user_spotify_export, language="fr")
        system_context = get_system_context(language="fr")

        if model_type == "openai":
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": system_context,
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            response_text = completion.choices[0].message.content
        elif model_type == "test":
            print(prompt)
            response_text = "Test Playlist\n$$$\nTest Description\n$$$"
        else:
            raise ValueError("Invalid model_type.")

        (
            playlist_name,
            playlist_description,
            generated_playlist_tracks,
        ) = self.parse_response(response_text)
        return playlist_name, playlist_description, generated_playlist_tracks

    def parse_response(self, response_text):
        parts = response_text.split("$$$")
        playlist_name = parts[0].strip()
        playlist_description = parts[1].strip()
        generated_playlist_tracks = [
            track.strip() for track in parts[2].strip().split("\n") if track.strip()
        ]
        return playlist_name, playlist_description, generated_playlist_tracks

    def create_user_playlist(
        self, playlist_name, playlist_description, generated_playlist_tracks
    ):
        user_id = self.spotipy.current_user()["id"]
        playlist = self.spotipy.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=playlist_description,
        )

        track_ids = self.get_track_ids(generated_playlist_tracks)
        if track_ids:
            self.spotipy.user_playlist_add_tracks(
                user=user_id, playlist_id=playlist["id"], tracks=track_ids
            )

    def modify_user_playlist(
        self, playlist_name, playlist_description, generated_playlist_tracks
    ):
        playlists = self.spotipy.current_user_playlists(limit=50)
        default_playlist_id = None
        for playlist in playlists["items"]:
            if playlist["name"] == playlist_name:
                default_playlist_id = playlist["id"]
                break

        if default_playlist_id:
            track_ids = self.get_track_ids(generated_playlist_tracks)
            self.spotipy.playlist_change_details(
                playlist_id=default_playlist_id,
                name=playlist_name,
                description=playlist_description,
            )
            self.spotipy.playlist_replace_items(
                playlist_id=default_playlist_id, items=track_ids
            )
        else:
            self.create_user_playlist(
                playlist_name, playlist_description, generated_playlist_tracks
            )

    def get_track_ids(self, generated_playlist_tracks):
        track_ids = []
        for track in generated_playlist_tracks:
            result = self.spotipy.search(q=track, type="track", limit=1)
            if result["tracks"]["items"]:
                track_ids.append(result["tracks"]["items"][0]["id"])
        return track_ids
