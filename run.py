import os

from dotenv import load_dotenv

from app import app

if os.path.exists(".env"):
    load_dotenv()

if __name__ == "__main__":
    app.run(
        threaded=True,
        port=int(os.getenv("SPOTIPY_REDIRECT_URI").split(":")[-1]),
        debug=True,
    )
