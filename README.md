# Ghost Jukebox

# Install

To install this on a Raspberry Pi equipped with a Pi Camera, first you need to install the requirements:

```sudo apt-get install build-essential libffi-dev libjpeg-dev libopenjp2-7 libssl-dev libzbar0 mplayer python-dev python3-pip python3-venv```

Then, just install this python package!

```python3 setup.py install```

# Idea

The idea of the Ghost Jukebox is twofold.
1. It should be like a Ghost - present yet unobtrusive and a bit magical
2. It should be like a Jukebox - you can play music on it

I was inspired by the fact that my roommate recently got a record player, and I like the record player. 
I like the physicality, the presence of each album and the beautiful cover art, the way one can browse through and choose a song.
I dislike the alternative: people fiddling with phones, choosing either to try and get bluetooth to work (it so rarely does that smoothly) or
to leave their phones physically connected to the speakers and periodically go over and fiddle with them some more.

But my roommate will move out and I will be left recordless, and anyways records are expensive and maintaining a good collection of them is hard. 
And thus was born: the Ghost Jukebox.

The basic components are: 
* A Raspberry Pi equipped with a camera
* An Amazon Echo Dot connected to speakers
* and a bunch of Cards representing some sort of Music

When a Card is placed in front of the camera of the Raspberry Pi, it should send a request to get the Amazon Echo Dot to play the music that the card represents.

Fun twists, though:
* The Card can represent an artist, album, song, playlist, or online radio station
* There will be two locations for the card to be slotted in, one which will simply play the thing, and the other which will generate a smart playlist based on what is referenced by the card
* I dunno, maybe if you turn the card sideways it plays it on shuffle?
* While I have the Raspberry Pi, might as well make a full-blown web interface for the thing to
    * Allows you to search the full Spotify catalog of albums, artists, tracks and playlists
    * Allows you to play, enqueue, or generate-a-playlist-from any of the aforementioned catalogs
    * Allows an easy manner in which to generate new cards (sneak preview - the cards have an album artwork on one side, and a QR code on the other)
* And hey - while I have a raspberry pi, lots of fun things I could do with that, like add a bunch of knobs and buttons
    * Next, back, play/pause buttons: obviously
    * Thumbs-up button: marks the song as a good one, saves it to your history/playlist/whatever
    * Random Playlist button: generates a playlist based on one of your most-listened-to artists, or something?
    * Knobs for: happiness, danciness, acousticness, tempo - apparently Spotify lets you specify these things when generating a smart playlist
    * Maybe a little display panel for what is currently playing

I haven't actually implemented all or much of any of that, but I think its a fun project!

## Design

### Hardware
I have a Raspberry Pi Zero ($5) running Raspbian Stretch Light, in the official Raspberry Pi camera case ($4) with a Raspberry Pi NoIR camera ($25) and a 32gb microSD card ($8) for storage.
It is plugged in the wall with a simple ($10) microUSB charging chord, and that is all!
I _will_ have a ($8) microHDMI - VGA + 3.5mil Audio converter, so that the Raspberry Pi can output sound. All in all, though: pretty cheap, especially compared to a record player!

And then, when all the software is satisfactory I will build what I am imagining to be a little wooden stand/dock type thing for the computer and the slots in which to put the cards. 
I am planning on getting a bunch of blank ID-sized PVC cards and printing out, on one side, album artwork (or whatever design I want to associate with a given playlist/track/artist/radio 
station) and then on the other side a cute little QR code for my camera to scan.

### Software
From back to front, on the Raspberry Pi Zero I am running NginX as a reverse proxy server, connected up to LetsEncrypt's Certbot for generating SSL connections. This talks to 
Gunicorn, which manages multiple worker threads of my Flask web app written in Python. The DB backing, currently very straightforward and minimal, is SQLite3. 

On the front-end, currently very *very* straightforward, is some raw HTML alongside the barest smatterings of raw JS and CSS rendered from Jinja templates in the Flask app and lightly styled with the help of Bootstrap and FontAwesome.
This may get sleeker over time. The current brevity seems like it may help with speed but for the great bottleneck of the Pi just _not being very fast_.

In general, when choosing technologies I wanted things that were a) pretty lightweight but b) very well used. I went with Python because that just seemed like the most Pi-esque way to go.
