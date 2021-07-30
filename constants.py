# stand lib
from pathlib import Path


DEBUG = False
SRC = str(Path.cwd())

BACKUPDIR = SRC + "/BACKUP"
HOME_PAGE = "https://www.lyrics.com"
PUNCTUATION = "/"
ROOT = "/" + "/".join(Path.cwd().parts[1:-1])
RESULTS = "results/"
SLEEP_TIME = 0.5
SUPPORT_DIR =  "support/"
TARS = "tars/"


#Lyrics.com specific routes
CATEGORY_ROUTE = "/artists/"
CATEGORY_ROUTE_REGEX = "^/artists/"
ARTIST_ROUTE_REGEX = "^artist/"
LYRIC_ROUTE_REGEX = "^/lyric/"
ALL_LINKS_SUFFIX = "/99999"


#Files supporting scraping
CATEGORY_DIR = SUPPORT_DIR + "category/"  
CATEGORY_ERRORS = SUPPORT_DIR + "categoryerrors.txt"
CATEGORIES = SUPPORT_DIR + "categories.txt"

ARTISTS = SUPPORT_DIR + "artists.txt"
ARTIST_DIR = SUPPORT_DIR + "artist/"
ARTIST_ERRORS = SUPPORT_DIR + "artist_errors.txt"
ARTISTS_SCRAPED = SUPPORT_DIR + "artists_scraped.txt"

SONGS = SUPPORT_DIR + "songs.txt"
SONG_DIR = SUPPORT_DIR + "song/"
SONG_ERRORS = SUPPORT_DIR + "song_errors.txt"
SONGS_SCRAPED = SUPPORT_DIR + "songs_scraped.txt"

LYRICS = SUPPORT_DIR + "lyrics.txt"
LYRICS_ERRORS = SUPPORT_DIR + "lyrics_errors.txt"
LYRICS_SCRAPED = SUPPORT_DIR + "lyrics_scraped.txt"


#For testing
LINE_COUNT_TEST = SRC + "/../testdata/countlinestest.txt"
LINK_STRING_TEST = "^/artists/"

#Support files
MANUALLY_CURATED = "manually_curated_words.txt"
DICTIONARY = "/usr/share/dict/web2"
CLEAN_DESC = SUPPORT_DIR + "clean_description.txt"
CLEAN_EPILOG = SUPPORT_DIR + "clean_epilog.txt"
DEMO_DESC = SUPPORT_DIR + "demo_description.txt"
DEMO_EPILOG = SUPPORT_DIR + "demo_epilog.txt"
GATHER_DESC = SUPPORT_DIR + "gather_description.txt"
SEARCH_DESC = SUPPORT_DIR + "search_description.txt"
SEARCH_EPILOG = SUPPORT_DIR + "search_epilog.txt"

#Tarballs
COMPRESSED_TESTING = f"{TARS}testing_compressed.tar.gz"
DEMO_TARBALL = f"demo/demo.tar"
ENG_TARBALL = f"{TARS}english_only.tar"
UNCOMPRESSED_TESTING = f"{TARS}testing_uncompressed.tar"
VOCAB_TARBALL = f"{TARS}vocabulary.tar"
