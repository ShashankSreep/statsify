import os
import string
import random
import time
from flask import Flask, redirect, request, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import json

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Generates a secret key for the application session
app.secret_key = ''.join(random.choices(string.ascii_letters, k=64))
app.config['SESSION_COOKIE_NAME'] = 'Shashanks Cookie'
TOKEN_INFO = "token_info"
TOKEN_INFO_FILE = 'token_info.json'

# Spotify credentials from the environment variables
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# Check if client_id and client_secret are set correctly
if not client_id or not client_secret:
    raise Exception("Missing CLIENT_ID or CLIENT_SECRET in the environment variables.")

# Scopes for Spotify application
scopes = [
    "user-read-email",
    "user-top-read",
    "user-read-currently-playing",
    "user-library-modify",
    "playlist-modify-public",
    "playlist-modify-private"
]

# Define the scopes string by joining the scopes list
scope = " ".join(scopes)
redirect_uri = "http://localhost:5000/callback/"

# Create Spotify OAuth scope
def create_oauth_scope():
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=url_for('callback', _external=True),
        scope=scope
    )
    return sp_oauth

@app.route("/")
def default_page():
    sp_oauth = create_oauth_scope()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = create_oauth_scope()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    with open(TOKEN_INFO_FILE, 'w') as f:
        json.dump(token_info, f)
    return "Authentication Complete!"

# Handle token retrieval and refreshing
def getToken():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise Exception('Token not found in session')
    
    # Refresh token if expired
    now = int(time.time())
    if token_info['expires_at'] - now < 60:
        sp_oauth = create_oauth_scope()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
    
    return token_info
if __name__ == "__name__":
    app.run(port=5000)
