# __init__.py

import os
import logging

from dotenv import load_dotenv
from flask import Flask
from flask_session import Session
from google.cloud import firestore

if os.path.exists(".env"):
    load_dotenv()

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = os.getenv("FLASK_SESSION_DIR")
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
Session(app)

# Connexion à Firestore
db = firestore.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"), database=os.getenv("FIRESTORE_DATABASE")
)

from app import views  # noqa: E402, F401
