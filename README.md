# Stone-Age to Spotify

Converts your audio file library to Spotify by scraping your audio files and their metadata to find the equivalent track on Spotify, which is then added to your Spotify library.

## Why?

After recently switching to Spotify as my main music provider, I realized that there was no efficient way to convert my old music (downloaded audio files) to Spotify.

Sure, you could drag them into your library, but that would only allow you to listen to them on the device that contained the audio sources and only on the desktop application.

I began searching for each song in my library, one-by-one on Spotify, adding them very slowly. I realized this was very inefficient.

I looked for a way to convert my library and found nothing, so I developed my own way.

## Resources

This application uses [Spotipy](http://spotipy.readthedocs.io/en/latest/#) - a lightweight Python library for the Spotify Web API.

The application also uses [Mutagen](https://mutagen.readthedocs.io/en/latest/) - a Python module used to handle audio metadata.

## How it Works

On first run, the application will open a URL to authenticate your Spotify account for the application to access your library.

The application will look for a /Music/ folder in the script's directory. If it does not exist, it will create one.

It will scrape the metadata of each audio file (title, artists). If an audio file does not contain any metadata, it will use the file name as the title.

After scraping the metadata, it will clean that data by trimming any website links and other redundant information for more accurate results.

It will then search Spotify using the title. Spotify will return a list of tracks.

The application will search through the artists of each track, using sequence matching to compare the Spotify song's artists to the local file's artists.

Once a match is found, the application will add the Spotify track to your Spotify library.