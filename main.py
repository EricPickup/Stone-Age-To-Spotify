import sys
import spotipy
import spotipy.util as util
import json
import os
import mutagen
import re

config = json.load(open('config.json'))

username = config["Spotify"]["username"]

scope = 'user-library-read user-modify-playback-state'

token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)


'''results = sp.search(q='track:' + sys.argv[1], limit=1, type='track')

print("Found song:")
track = results['tracks']['items'][0]
print("Track URI: ", track['uri'])
print("Title: ", track['name'])
print("Artist: ", track['artists'][0]['name'])
print("\n\nNOW PLAYING...")


uris = [track['uri']]
sp.start_playback(uris=uris)'''


def stripTitle(title):

		if 'Flo' in title:
			print("**** BEFORE: %s" % title)

		#Removing parantheses and characters inside of them (ex: (feat. Artist) or (www.piratewebsite.com))
		title = re.sub('\(.*\)', '', title)

		#Removing file extensions (seeks any period (.) followed by any 3 characters - ex: .wma)
		title = re.sub('\.[a-zA-Z0-9]{3}$', '', title)

		#Removing website likes
		title = re.sub('www\.[a-zA-Z0-9]*\.[a-zA-Z]{2,3}', '', title)

		title.replace('_', ' ')

	
		print(title)



if (os.path.isdir("Music")):
	path, dirs, files = next(os.walk("Music"))
	file_count = len(files)
	print("Found music folder containing %d files" % file_count)
else:
	print("Music folder not found...")
	os.makedirs("Music")
	print("Created music folder in script's directory, add songs to folder")
	print("Exiting...")
	sys.exit()



files = os.listdir("Music")
for song in files:
	audio = mutagen.File("Music/" + song, easy=True)
	title = ''
	if ('title' in audio):
		title = audio['title'][0]
	else:
		title = song
	stripTitle(title)
