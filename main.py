import sys
import spotipy
import spotipy.util as util
import json
import os
import mutagen
import re
from difflib import SequenceMatcher


class Song:

	def __init__(self, title, path, artist):
		self.title = title
		self.artist = artist
		self.path = path


def stripTitle(title):
		#Removing parantheses and characters inside of them (ex: (feat. Artist) or (www.piratewebsite.com))
		title = re.sub('\(.*\)', '', title)

		#Removing file extensions (seeks any period (.) followed by any 3 characters - ex: .wma)
		title = re.sub('\.[a-zA-Z0-9]{3}$', '', title)

		#Removing URLs (preceding www. followed by any characters)
		title = re.sub('www\.[a-zA-Z0-9-/\.]*', '', title)

		#Removing URLs without preceding www. 
		title = re.sub('[a-zA-Z0-9-]+\.[a-zA-Z]{2,3}(/[a-zA-Z0-9]*)*', '', title)

		#Replacing all underscores with spaces, ex: Let_It_Be_The_Beatles.mp3 (common with pirated music)
		title = title.replace('_', ' ')
		title = title.replace('-', ' ')

		return title

def stripArtists(artist):
	#Stripping any features from artist's name (only one artists' match is needed, having multiple in one search decreases matches as we compare to one artist at a time)
	artist = re.sub('ft\..*$', '', artist)
	artist = re.sub('Ft\..*$', '', artist)
	artist = re.sub('feat\..*$', '', artist)
	artist = re.sub('Feat\..*$', '', artist)

	#Removing URLs (preceding www. followed by any characters)
	title = re.sub('www\.[a-zA-Z0-9-/\.]*', '', artist)
	#Removing URLs without preceding www. 

	title = re.sub('[a-zA-Z0-9-]+\.[a-zA-Z]{2,3}(/[a-zA-Z0-9]*)*', '', artist)

	return artist


def checkForMusicFolder():
	#If program directory contains "Music" folder
	if (os.path.isdir("Music")):
		path, dirs, files = next(os.walk("Music"))
		file_count = len(files)
		print("Found music folder containing %d files" % file_count)
	#If not, create one and exit program so user can populate music folder
	else:
		print("Music folder not found...")
		os.makedirs("Music")
		print("Created music folder in script's directory, add songs to folder")
		print("Exiting...")
		sys.exit()


def scrapeSongs():
	#Gather list of files in Music directory
	files = os.listdir("Music")
	
	songs = []

	for song in files:

		currentFilePath = "Music/" + song

		#If current file is a directory, skip
		if (os.path.isdir(currentFilePath)):
			continue

		audio = mutagen.File(currentFilePath, easy=True)
		title = ''

		#If current file is not a compatible audio file, skip
		if (audio is None):
			continue
		#If the song contains title metadata, use that as song title
		elif ('title' in audio):
			title = audio['title'][0]

		#Otherwise use the file name as the song title
		else:
			title = song

		#If the audio file contains the artist metadata, store it in the object
		if ('artist' in audio):
			currentSong = Song(title, currentFilePath, audio['artist'][0])
		else:
			currentSong = Song(title, currentFilePath, '')

		songs.append(currentSong)

	return songs


def findMatch(sp, localSong):

	results = sp.search(q='track:' + localSong.title, limit=15, type='track')
	spotifySongs = results['tracks']['items']
	matched = False

	#If songs were found
	if spotifySongs:
		#First results is most likely to be correct, start there
		matchedSong = spotifySongs[0]
		artistConfidence = 0.0

		#If the local audio file has an artist name
		if (localSong.artist != ''):
			#For every song returned from Spotify
			for spotifySong in spotifySongs:

				#If a song was found, break out of loop (couldn't break from a nested loop)
				if matched == True:
					break

				print("Testing for: \"%s\" by %s" % (spotifySong['name'], spotifySong['artists'][0]['name']))

				#Compare each artist of the spotify song being checked to the local song's artist
				for spotifyArtist in spotifySong['artists']:

					artistComparisonConfidence = compareStrings(spotifyArtist['name'], localSong.artist)
					print("Compared to %s: %f" % (spotifyArtist['name'], artistComparisonConfidence))

					#If artist match is a maybe... (40-60% confidence)
					if (artistComparisonConfidence > 0.45 and artistComparisonConfidence < 0.6):
						#Check how similar the spotify song title is to the local song title to be sure
						if (compareStrings(spotifySong['name'], localSong.title) > 0.6):
							matchedSong = spotifySong
							matched = True
							break

					#Otherwise if the artist is most likely correct (>= 60% confidence)
					elif (artistComparisonConfidence >= 0.6):
						matchedSong = spotifySong
						matched = True
						break

		#If we don't know the artist's name (local file does not have artist), and the song names are similar (>60%), assume correct
		else:
			for spotifySong in spotifySongs:
				if compareStrings(spotifySong['name'], localSong.title) > 0.6:
					matched = True
					break
		
	if (matched == True):
		return matchedSong
	else:
		return None


def compareStrings(spotifyArtist, songArtist):
	return SequenceMatcher(None, spotifyArtist, songArtist).ratio()



def main():

	config = json.load(open('config.json'))
	username = config["Spotify"]["username"]

	scope = 'user-read-private user-library-modify'

	token = util.prompt_for_user_token(username, scope)

	if token:
	    sp = spotipy.Spotify(auth=token)

	checkForMusicFolder()

	songs = scrapeSongs()

	for song in songs:
		song.title = stripTitle(song.title)
		if (song.title != ''):
			song.artist = stripArtists(song.artist)

	for song in songs:
		songsToAdd = []
		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		if (song.artist != ''):
			print("Searching for: %s by %s" % (song.title, song.artist))
		else:
			print("Searching for: %s" % song.title)
		print("SPOTIFY:")
		match = findMatch(sp, song)
		if match is None:
			print("No match found.")
		else:
			print("Match found:\nTitle: %s\nAuthor: %s\nSpotify URI: %s" % (match['name'], match['artists'][0]['name'], match['uri']))
			songsToAdd.append(match['uri'])
			sp.current_user_saved_tracks_add(tracks=songsToAdd)

		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")

		

if  __name__ =='__main__':main()

