import sys
import spotipy
import spotipy.util as util
import json

config = json.load(open('config.json'))

username=config["Spotify"]["username"]

scope = 'user-library-read user-modify-playback-state'

token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)


results = sp.search(q='track:' + sys.argv[1], limit=1, type='track')

print("Found song:")
track = results['tracks']['items'][0]
print("Track URI: ", track['uri'])
print("Title: ", track['name'])
print("Artist: ", track['artists'][0]['name'])
print("\n\nNOW PLAYING...")


uris = [track['uri']]
sp.start_playback(uris=uris)
