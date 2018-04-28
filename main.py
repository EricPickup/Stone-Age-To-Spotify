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

		#Removing website likes
		title = re.sub('www\.[a-zA-Z0-9]*\.[a-zA-Z]{2,3}', '', title)

		#Replacing all underscores with spaces, ex: Let_It_Be_The_Beatles.mp3 (common with pirated music)
		title = title.replace('_', ' ')

		return title


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
			print("***Found incompatible folder: %s" % song)
			continue

		audio = mutagen.File(currentFilePath, easy=True)
		title = ''

		#If current file is not a compatible audio file, skip
		if (audio is None):
			print("***Found incompatible file: %s" % song)
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


def findMatch(sp, song):
	results = sp.search(q='track:' + song.title, limit=15, type='track')
	matchFlag = 0
	if results['tracks']['items']:
		bestTrack = results['tracks']['items'][0]
		artistConfidence = 0.0
		if (song.artist != ''):
			for resultSong in results['tracks']['items']:
				if matchFlag == 1:
					break
				print("Testing for song %s" % resultSong['name'])
				for artist in resultSong['artists']:
					artistComparisonConfidence = compareStrings(artist['name'], song.artist)
					print("\tTrying artist: %s, confidence: %f" % (artist['name'], artistComparisonConfidence))
					if (artistComparisonConfidence > 0.4):
						bestTrack = resultSong
						matchFlag = 1
						break
		else:
			matchFlag = 1
		
	if (matchFlag == 1):
		print("Found song:")
		print("Track URI: ", bestTrack['uri'])
		print("Title: ", bestTrack['name'])
		print("Artist: ", bestTrack['artists'][0]['name'])
		return bestTrack['artists'][0]['name']
	else:
		print("match not found")


def compareStrings(spotifyArtist, songArtist):
	return SequenceMatcher(None, spotifyArtist, songArtist).ratio()



def main():

	config = json.load(open('config.json'))
	username = config["Spotify"]["username"]

	scope = 'user-modify-playback-state'

	token = util.prompt_for_user_token(username, scope)

	if token:
	    sp = spotipy.Spotify(auth=token)

	checkForMusicFolder()

	songs = scrapeSongs()

	for song in songs:
		song.title = stripTitle(song.title)

	for song in songs:
		print("############################################")
		print(song.title)
		if (song.artist != ''):
			print(song.artist)
		print("SPOTIFY: ")
		findMatch(sp, song)
		

if  __name__ =='__main__':main()

