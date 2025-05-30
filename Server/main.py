import json
import time
import os
from spotipy import Spotify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN_INFO_FILE = "token_info.json"

# Gets the token information
# In the case that the token needs to be refreshed, handles that as well
# prompting the user to authenticate with the Flask server
def get_token():
    # Wait until token info is available
    while not os.path.exists(TOKEN_INFO_FILE):
        print("Please authenticate via the Flask server...")
        time.sleep(5)
    # Load token info
    with open(TOKEN_INFO_FILE, 'r') as f:
        token_info = json.load(f)
    return token_info


# Method to retrieve user information
# Gets the Display Name of the user
# Gets the Email and user_id
def getUserInfo():
    token_info = get_token()
    sp = Spotify(auth=token_info['access_token'])
    user_data = sp.me()
    res = [user_data.get('display_name'), user_data.get('email'), user_data.get('id')]
    return res

# Gets top 10 tracks for a certain time period as specificed by the user
def get_top_tracks(term):
    terms = {'short_term', 'long_term', 'medium_term'}
    if term not in terms:
        return []
    token_info = get_token()
    sp = Spotify(auth=token_info['access_token'])
    tracks = sp.current_user_top_tracks(10, 0, term)['items']
    res = []
    for track in tracks:
        res.append(track['name'] + ' - ' + track['album']['name'])
    return res

# get currently playing track
def getCurrTrack():
    token_info = get_token()
    sp = Spotify(auth=token_info['access_token'])
    res = sp.current_user_playing_track()
    track = ""
    if res:
        track = res['item']['name'] + ' - ' + res['item']['album']['name']
    return track if res and res['item'] else ""

# Creates a new blank playlist for the current user
# Depending on the user input, they can choose private or public
def createBlankPlaylist(user_id, name, public):
    isPublic = False
    if public == 'public': isPublic = True
    token_info = get_token()
    sp = Spotify(auth=token_info['access_token'])
    sp.user_playlist_create(user_id, name, isPublic)
    return

# We will get the top x # of tracks
# get the track uri for each track
def get_track_uri(num_tracks):
    token_info = get_token()
    sp = Spotify(auth=token_info['access_token'])
    res = [] # list of track_uri's
    tracks = sp.current_user_top_tracks(num_tracks, 0, 'short_term')['items']
    for track in tracks:
        res.append(track["id"])
    return res # list of track_uri's
    


# Creates a new playlist, for the user, with their top X # of tracks
# Depending on their choice for public or private
def addPlaylist(user_id, num_tracks):
    token_info = get_token()
    sp = Spotify(auth=token_info['access_token'])

    tracks_to_add = get_track_uri(num_tracks) # gets the track_uri's    
    # First, Create a new playlist
    playlist = sp.user_playlist_create(user_id, 'Top Tracks',
                                    False, False, "Top tracks")
    playlist_id = playlist['id']
    sp.playlist_add_items(playlist_id, tracks_to_add)
    return

def get_top_artists():
    token_info = get_token()
    sp = Spotify(auth=token_info['access_token'])
    res = []
    artists = sp.current_user_top_artists(5, 0, "short_term")['items']
    for artist in artists:
        res.append(artist['name'])
    return res

# Handles creating and writing to a file
# This way, the user can view their statistics in a readable format 
# All at once!
def handle_file_write(user_name):
    # 1) Write the User Profile
    top_songs = get_top_tracks('short_term')
    top_artists = get_top_artists()
    with open("statsify.txt", "w") as file:
        file.write("Hello, " + user_name + "! Here is your Statsify Recap!\n")
        file.write('///////////////////////////////////////////////////////\n')
        file.write('\n')
        file.write("Your top 10 songs for the past 1 month!\n")
        for i in range(1, 11):
            file.write(str(i) + ') ' + top_songs[i - 1] + '\n')
        file.write('\n')
        file.write('///////////////////////////////////////////////////////\n')
        file.write('\n')
        file.write("Your top Artists for the past 1 month!\n")
        for i in range(1, 6):
            file.write(str(i) + ') ' + top_artists[i - 1] + '\n')
        file.write('\n')
        file.write('///////////////////////////////////////////////////////\n')
    return

# handles all of the user input
def main():
    user_data = getUserInfo()
    user_name = user_data[0]
    print("Hello " + user_name + "! Welcome to Statsify!")
    print()
    while True:
        print("Enter 'user' to access user information")
        print("Enter 'tracks' to access your top tracks")
        print("Enter 'curr' to get your current track!")
        print("Enter 'custom_add' to add your top 10 songs to a playlist")
        print("Enter 'create' to create a new playlist")
        print("Enter 'artists' to get your top artists")
        print("Enter 'q' to quit!")
        print()
        action = input()
        if action == 'user':
            # get user information
            print("Here is your information, " + user_name)
            print("----------------------------------")
            print("User Name: " + user_data[0])
            print("Email: " + user_data[1])
            print("User_ID: " + user_data[2])
            print()
        elif action == 'tracks':
            print("How recent would you like your tracks to be?" +
                  "'short_term', 'medium_term', 'long_term'")
            term = input()
            print("Retrieving Top Tracks for " + user_data[0])
            print("-----------------------------------")
            tracks = get_top_tracks(term)
            for i, track in enumerate(tracks):
                print(str(i + 1) + ") " + track)
            print()
        elif action == 'curr':
            cur_track = getCurrTrack()
            if cur_track:
                print("You are currently listening to: " + cur_track)
            else:
                print("You are not currently listening to anything!")
            print()
        elif action == 'create':
            print("Would you like to create a 'public' or 'private' playlist?")
            public = input()
            print("What is the name of your playlist?")
            name = input()
            createBlankPlaylist(user_data[2], name, public)
            print("Playlist Successfully created!")
        elif action == 'custom_add':
            print("How many top tracks would you like to add?")
            num_tracks = input()
            if int(num_tracks) > 50:
                print("Too many tracks: Please select 1 - 50 tracks")
                num_tracks = input()
            addPlaylist(user_data[2], num_tracks)
            print("Successfully Added!")
        elif action == 'artists':
            get_top_artists()
        elif action == 'q':
            print("Would you like to save your statistics to a file? (Y/N)")
            i = input()
            if i == 'Y':
                handle_file_write(user_data[0])
                print("Please view your statistics in your file!")
            break
        else:
            print('Please enter a valid action!')
if __name__ == "__main__":
    main()
