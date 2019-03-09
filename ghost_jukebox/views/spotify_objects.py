import requests

class Artist:
    def __init__(
        self, 
        uri, 
        name, 
        spotify_link, 
        genres = None, 
        followers = None, 
        image_set = None,
        popularity = None
    ):
        self.uri = uri
        self.name = name
        self.genres = genres
        self.spotify_link = spotify_link
        self.followers = followers
        self.image_set = image_set
        self.popularity = popularity

def artist_from_json(info):
    try:
        return Artist(
            uri = info['uri'],
            name = info['name'],
            spotify_link = info['external_urls']['spotify'] if 'spotify' in info['external_urls'] else None,
            genres = info['genres'] if 'genres' in info else None,
            followers = info['followers']['total'] if 'followers' in info else None,
            image_set = image_set_from_json(info['images']) if 'images' in info else None,
            popularity = info['popularity'] if 'popularity' in info else None
        )
    except:
        return False

class Album:
    def __init__(
        self, 
        uri, 
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
        self.uri          = uri
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

def album_from_json(info):
    try:
        return Album(
            uri = info['uri'],
            album_type = info['album_type'],
            name = info['name'],
            release_date = info['release_date'],
            artists = remove_empties([artist_from_json(artist) for artist in info['artists']]),
            spotify_link = info['external_urls']['spotify'] if 'spotify' in info['external_urls'] else None,
            genres = info['genres'] if 'genres' in info else None,
            image_set = image_set_from_json(info['images']) if 'images' in info else None,
            tracks = remove_empties([track_from_json(track) for track in info['tracks']]) if 'tracks' in info else None,
            label = info['label'] if 'label' in info else None,
            popularity = info['popularity'] if 'popularity' in info else None
        )
    except:
        return False

def Track:
    def __init__(
        self,
        uri,
        name,
        artists,
        duration_ms,
        track_number,
        is_explicit,        
        preview_url = None,
        album = None,
        popularity = None
    ):
        self.uri          = uri
        self.name         = name
        self.artists      = artists
        self.duration_ms  = duration_ms
        self.track_number = track_number
        self.is_explicit  = is_explicit
        self.preview_url  = preview_url
        self.album        = album
        self.popularity   = popularity

def track_from_json(info):
    try:
        return Track(
            uri = info['uri'],
            name = info['name'],
            artists = remove_empties([artist_from_json(artist) for artist in info['artists']]),
            spotify_link = info['external_urls']['spotify'] if 'spotify' in info['external_urls'] else None,
            duration_ms = int(info['duration_ms']),
            track_number = int(info['track_number']),
            is_explicit = info['explicit'],
            preview_url = info['preview_url'] if 'preview_url' in info else None,
            album = album_from_json(info['album']) if 'album' in info else None,
            popularity = info['popularity'] if 'popularity' in info else None
        )
    except:
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
    except:
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
