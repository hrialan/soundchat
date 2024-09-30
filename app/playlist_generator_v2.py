# playlist_generator.py

import os

import spotipy
from dotenv import load_dotenv
from openai import OpenAI

if os.path.exists(".env"):
    load_dotenv()


class PlaylistGenerator:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.spotipy = spotipy.Spotify(auth_manager=self.auth_manager)

    def ask_playlist_recommendation_seeds(self, user_context, model_type="openai"):
        prompt = f"""
        Hi there ! Can you please help me create a playlist for me ?
        I will give you a context and you will generate the seeds for the spotify recommendation algorithm.
        I will then create a playlist based on the generated seeds.
        Context: {user_context}

        **Response Format**:
        "
        Tracks seed list
        $$$
        Artists seed list
        $$$
        Genres seed list
        $$$
        danceability float
        $$$
        energy float
        "

        Thanks in advance !
        """

        if model_type == "openai":
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a seasoned music connoisseur with an extensive knowledge of diverse genres and a keen ability to curate playlists that resonate deeply with listeners. Your mission is to craft an exceptional playlist that will captivate a broad audience, taking into account their current mood and detailed Spotify listening history. You are dedicated to understanding the nuances of each user's musical preferences, ensuring a personalized and emotionally engaging listening experience for everyone.",
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

        print(response_text)
        (tracks_seed, artists_seed, genres_seed, danceability, energy) = (
            self.parse_response(response_text)
        )

        return tracks_seed, artists_seed, genres_seed, danceability, energy

    def parse_response(self, response_text):
        parts = response_text.split("$$$")
        tracks_seed = parts[0].strip()
        artists_seed = parts[1].strip()
        genres_seed = parts[2].strip()
        danceability = parts[3].strip()
        energy = parts[4].strip()
        return tracks_seed, artists_seed, genres_seed, danceability, energy

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

    def test_spotify_recommendations(self):
        recommendations = self.spotipy.recommendations(
            seed_tracks=["0c6xIDDpzE81m2q797ordA"], limit=5
        )
        self.create_user_playlist(
            "Test Recommendations",
            "Test Recommendations",
            [
                f"{track['name']} - {track['artists'][0]['name']}"
                for track in recommendations["tracks"]
            ],
        )


if __name__ == "__main__":
    from dotenv import load_dotenv

    if os.path.exists(".env"):
        load_dotenv()

    SPOTIFY_SCOPES = "playlist-read-private,playlist-modify-private,user-top-read,user-library-read,user-follow-read,user-read-recently-played"

    auth_manager = spotipy.oauth2.SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=SPOTIFY_SCOPES,
    )

    playlist_generator = PlaylistGenerator(auth_manager)
    playlist_generator.ask_playlist_recommendation_seeds(
        "Année 80", model_type="openai"
    )
