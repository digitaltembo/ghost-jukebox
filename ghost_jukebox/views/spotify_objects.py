import requests
from ghost_jukebox.app import logger
from flask import url_for, Markup, escape

class Artist:
    def __init__(
        self, 
        id, 
        name, 
        spotify_link, 
        genres = None, 
        followers = None, 
        image_set = None,
        popularity = None
    ):
        self.id = id
        self.name = name
        self.genres = genres
        self.spotify_link = spotify_link
        self.followers = followers
        self.image_set = image_set
        self.popularity = popularity
    def url(self):
        return url_for('artist_info', artist_id = self.id)
    def link(self):
        return Markup("<a href='{}' class='artist-link'>{}</a>".format(self.url(), escape(self.name)))

def artist_from_json(info):
    try:
        return Artist(
            id = info['id'],
            name = info['name'],
            spotify_link = info['external_urls']['spotify'] if 'spotify' in info['external_urls'] else None,
            genres = info['genres'] if 'genres' in info else None,
            followers = info['followers']['total'] if 'followers' in info else None,
            image_set = image_set_from_json(info['images']) if 'images' in info else None,
            popularity = info['popularity'] if 'popularity' in info else None
        )
    except Exception:
        logger.exception('Could not parse artist from {}')
        return False

class Album:
    def __init__(
        self, 
        id, 
        album_type, 
        name, 
        release_date, 
        artists, 
        spotify_link, 
        genres = None, 
        image_set = None, 
        tracks = None, 
        label = None,
        popularity = None
    ):
        self.id          = id
        self.album_type   = album_type
        self.name         = name
        self.release_date = release_date
        self.artists      = artists
        self.spotify_link = spotify_link
        self.genres       = genres
        self.image_set    = image_set
        self.tracks       = tracks
        self.label        = label
        self.popularity   = popularity
    def url(self):
        return url_for('album_info', album_id = self.id)
    def link(self):
        return Markup("<a href='{}' class='album-link'>{}</a>".format(self.url(), escape(self.name)))
    def artist_links(self):
        return [artist.link() for artist in self.artists]

def album_from_json(info):
    try:
        return Album(
            id = info['id'],
            album_type = info['album_type'],
            name = info['name'],
            release_date = info['release_date'],
            artists = remove_empties([artist_from_json(artist) for artist in info['artists']]),
            spotify_link = info['external_urls']['spotify'] if 'spotify' in info['external_urls'] else None,
            genres = info['genres'] if 'genres' in info else None,
            image_set = image_set_from_json(info['images']) if 'images' in info else None,
            tracks = remove_empties([track_from_json(track) for track in info['tracks']['items']]) if 'tracks' in info else None,
            label = info['label'] if 'label' in info else None,
            popularity = info['popularity'] if 'popularity' in info else None
        )
    except Exception:
        logger.exception('Could not parse album from {}')
        return False

class Track:
    def __init__(
        self,
        id,
        name,
        artists,
        duration_ms,
        track_number,
        spotify_link,
        is_explicit,        
        preview_url = None,
        album = None,
        popularity = None
    ):
        self.id          = id
        self.name         = name
        self.artists      = artists
        self.duration_ms  = duration_ms
        self.track_number = track_number
        self.is_explicit  = is_explicit
        self.preview_url  = preview_url
        self.album        = album
        self.popularity   = popularity
    def url(self):
        return url_for('track_info', track_id = self.id)
    def link(self):
        return Markup("<a href='{}' class='track-link'>{}</a>".format(self.url(), escape(self.name)))

def track_from_json(info):
    try:
        return Track(
            id = info['id'],
            name = info['name'],
            artists = remove_empties([artist_from_json(artist) for artist in info['artists']]),
            duration_ms = int(info['duration_ms']),
            track_number = int(info['track_number']),
            spotify_link = info['external_urls']['spotify'] if 'spotify' in info['external_urls'] else None,
            is_explicit = info['explicit'],
            preview_url = info['preview_url'] if 'preview_url' in info else None,
            album = album_from_json(info['album']) if 'album' in info else None,
            popularity = info['popularity'] if 'popularity' in info else None
        )
    except Exception:
        logger.exception('Could not parse track from {}')
        return False

class Playlist:
    def __init__(
        self,
        id,
        name,
        owner,
        spotify_link,
        image_set = None,
        tracks = [],
        description = None,

    ):
        self.id           = id
        self.name         = name
        self.owner        = owner
        self.spotify_link = spotify_link
        self.image_set    = image_set
        self.tracks       = tracks
        self.description  = description
    def url(self):
        return url_for('playlist_info', playlist_id = self.id)
    def link(self):
        return Markup("<a href='{}' class='playlist-link'>{}</a>".format(self.url(), escape(self.name)))

def playlist_from_json(info):
    try:
        return Playlist(
            id = info['id'],
            name = info['name'],
            ownder = user_from_json(info['owner']),
            spotify_link = info['external_urls']['spotify'] if 'spotify' in info['external_urls'] else None,
            image_set = image_set_from_json(info['images']) if 'images' in info else None,
            tracks = remove_empties([track_from_json(playlist_track['track']) for playlist_track in info['tracks']['items']]) if 'tracks' in info else [],
            description = info['description'] if 'description' in info else None
        )
    except Exception:
        logger.exception('Could not parse playlist from {}')
        return False


class User:
    def __init__(
        self,
        id,
        name, 
        image_set,
        spotify_link,
        playlists = []
    ):
        self.id           = id
        self.name         = name
        self.image_set    = image_set
        self.spotify_link = spotify_link
        self.playlists    = playlists

    def url(self):
        return url_for('user_info', user_id = self.id)
    def link(self):
        return Markup("<a href='{}' class='user-link'>{}</a>".format(self.url(), escape(self.name)))

def user_from_json(info):
    try:
        return User(
            id = info['id'],
            name = info['display_name'],
            image_set = image_set_from_json(info['images']) if 'images' in info else None,
            spotify_link = info['external_urls']['spotify'] if 'spotify' in info['external_urls'] else None
        )
    except Exception:
        logger.exception('Could not parse user from {}')
        return False

class Image:
    def __init__(self, url, width, height):
        self.url = url
        self.width = width
        self.height = height

def image_from_json(info):
    try:
        url = info['url']
        width = int(info['width'])
        height = int(info['height'])
        return Image(url, width, height)
    except Exception:
        logger.exception('Could not parse image from {}')
        return False

class ImageSet:
    def __init__(self, images):
        self.images = images 

    def get_by_size(self, width = None, target_height = None):
        width_delta = lambda img: abs(img.width - target_width)
        height_delta = lambda img: abs(img.height - target_height)
        delta = 100000
        to_return = self.images[0]
        if target_width == None and target_height == None:
            return to_return
        elif target_width == None:
            for img in self.images:
                if height_delta(img) < delta:
                    delta = height_delta(img)
                    to_return = img 
        elif target_height == None:
            for img in self.images:
                if width_delta(img) < delta:
                    delta = width_delta(img)
                    to_return = img 
        else:
            for img in self.images:
                if width_delta(img) + height_delta(img) < delta:
                    delta = width_delta(img) + height_delta(img)
                    to_return = img 
        return to_return

def image_set_from_json(info):
    return remove_empties([image_from_json(img) for img in info])

def remove_empties(lizt):
    return filter(lambda i: i, lizt)

