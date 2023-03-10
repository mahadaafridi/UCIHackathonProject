import json
import time
import urllib.parse
import urllib.request
import requests
import pandas as pd
# To do things change the playlist ids of the genres dictionary

CLIENT_ID = 'b38bdc06ca494cd385eaf026a84f53fd'
CLIENT_SECRET = '4418182ed9b447e8a142063574c5c347'

genres = {'more-songs-1': (#'37i9dQZF1DWXRqgorJj26U',
                            # "40y8L7CXfZYv8zgMB9asj7",
                            # "40HuXUhGne38mfewzlLghz",
                            # "3a9pVhH8G93BZ3OB9OTbhF",
                            # "2X669hlkIwJ5GZaz27dG7c",
                            # "69tUdeFaKRDVTg2guSDttx,
                               "61BMAa1lb86F6QTs1MA6n4",
                            )
                            }

def get_token() -> str:
    AUTH_URL = 'https://accounts.spotify.com/api/token'
    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    # convert the response to JSON
    auth_response_data = auth_response.json()
    # save the access token
    return auth_response_data['access_token']

def create_header() -> dict:
    access_token = get_token()
    headers = {
        'Authorization': 'Bearer {token}'.format(token = access_token)
    }
    return headers

def get_song_features(song_id: str) -> tuple:
    # base URL of all Spotify API endpoints
    BASE_URL = 'https://api.spotify.com/v1/'
    # Track ID from the URI
    track_id = song_id
    # actual GET request with proper header
    headers = create_header()
    r = requests.get(BASE_URL + 'audio-features/' + track_id, headers = headers)
    r = r.json()
    dance = r['danceability']
    energy = r['energy']
    key = r['key']
    loudness = r['loudness']
    speechiness = r['speechiness']
    acousticness = r['acousticness']
    instrumentalness = r['instrumentalness']
    liveness = r['liveness']
    valence = r['valence']
    tempo = r['tempo']
    return track_id, dance, energy, key, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo


def get_playlist(playlist_id: str) -> list:
    """ Returns a list of song ids in a playlist """
    BASE_URL = 'https://api.spotify.com/v1/playlists/'
    # actual GET request with proper header
    headers = create_header()
    r = requests.get(BASE_URL + playlist_id + '/tracks?market=US', headers = headers)
    r = r.json()
    items = r['items']
    ids = []
    for track in items:
        ids.append(track['track']['id'])
    while True:
        try:
            r = requests.get(r['next'],
                             headers = headers)
            r = r.json()
            items = r['items']
            for track in items:
                try:
                    ids.append(track['track']['id'])
                except:
                    pass
        except:
            break
    return ids

def get_features_of_playlist(playlist_song_id_list: list) -> list['tuple']:
    """ Returns the features of a playlist"""
    playlist_features_list = []
    for song in playlist_song_id_list:
        try:
            playlist_features_list.append(get_song_features(song))
        except:
            pass
    return playlist_features_list

def get_features_for_genre():
    temp_genres = genres.copy()
    for genre, ids in temp_genres.items():
        features_of_genre = []
        for playlist_id in ids:
            song_list = get_playlist(playlist_id)
            features_of_songs_in_playlist = get_features_of_playlist(song_list)
            features_of_genre.extend(features_of_songs_in_playlist)
            time.sleep(20)
        no_dups = set(features_of_genre)
        list_no_dups = list(no_dups)
        temp_genres[genre] = list_no_dups
        print(genre)
    return temp_genres

def create_csv_files():
    # Takes in all the playlist ids from the genres dict and
    # makes csvs of each genre and the songs inside the playlist
    temp_genre = get_features_for_genre()
    i = 7
    for key, val in temp_genre.items():
        file = f'{key}-{i}.csv'
        df = pd.DataFrame(val, columns = ['track_id',
                                          'danceability',
                                          'energy',
                                          'key',
                                          'loudness',
                                          'speechiness',
                                          'acousticness',
                                          'instrumentalness',
                                          'liveness',
                                          'valence',
                                          'tempo'])
        df.to_csv(file)
        i += 1

if __name__ == '__main__':
    create_csv_files()