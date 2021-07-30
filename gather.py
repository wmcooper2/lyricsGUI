# std lib
import argparse
import io
import os
from pathlib import Path
from pprint import pprint
import re
from requests.exceptions import SSLError
from ssl import SSLEOFError
from string import ascii_uppercase as uppercase
from string import ascii_letters as letters
import tarfile
from urllib.parse import unquote_plus
from urllib3.exceptions import MaxRetryError

# custom
from scrapeutil import (
    format_artist_link,
    format_category_link,
    format_song_link,
    get_artist,
    get_links,
    get_lyrics,
    get_song,
    get_soup,
    load_file_list)

from constants import (
    ALL_LINKS_SUFFIX,
    ARTISTS,
    ARTIST_ERRORS,
    ARTISTS_SCRAPED,
    ARTIST_ROUTE_REGEX,
    CATEGORIES,
    CATEGORY_ROUTE_REGEX,
    GATHER_DESC,
    HOME_PAGE,
    LYRIC_ROUTE_REGEX,
    LYRICS_ERRORS,
    LYRICS_SCRAPED,
    SONGS,
    SONGS_SCRAPED,
    SUPPORT_DIR)



#TODO, add option for manually handling the artist, song, lyric scraping errors
#TODO, add option for resetting the scraping files for each step

if __name__ == "__main__":

    #Load description
    with open(GATHER_DESC) as f:
        how_to_use = f.read()
    
    parser = argparse.ArgumentParser(prog="Gather", formatter_class=argparse.RawDescriptionHelpFormatter, description=how_to_use)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--categories", action="store_true", help="Scrape and save the A-Z category links from lyrics.com")
    group.add_argument("--artists", action="store", nargs="*", type=str, metavar=("CATEGORY"), help="Scrape artist links from specific categories.")
    group.add_argument("--allartists", action="store_true", help="Scrape artist links from all A-Z and 0 (#) categories.")
    group.add_argument("--artisterrors", action="store_true", help="Manually fix the artist links that couldn't be handled by the program.")
    group.add_argument("--songs", action="store_true", help="Scrape and save the song links within each artists page from lyrics.com")
    group.add_argument("--songerrors", action="store_true", help="Manually fix the song links that couldn't be handled by the program.")
    group.add_argument("--lyrics", action="store_true", help="Scrape and save the lyrics from each song link from lyrics.com")
    args = parser.parse_args()

    #Files and Dirs Check
    Path(SONGS).touch(exist_ok=True)
    Path(ARTISTS_SCRAPED).touch(exist_ok=True)
    Path(LYRICS_SCRAPED).touch(exist_ok=True)


#CATEGORIES
    if args.categories: 
        print("--- SCRAPING CATEGORIES ---")
        soup = get_soup(HOME_PAGE)
        links = get_links(soup, CATEGORY_ROUTE_REGEX)
        print(f"A-tag example: {links[1]}")  # show example
        print(f"Saved URL example: {format_category_link(links[1])}")  # show example
        with open(CATEGORIES, "w+") as categories:
            for link in map(format_category_link, links):
                categories.write(link+"\n")
        print("--- SCRAPING CATEGORIES FINISHED ---")



#ARTISTS
    #Scrape only the artist categories the user specifies
    elif args.artists:
        print("--- SCRAPING ARTISTS ---")
        #Operate on all the given categories in args
        try:
            with open(f"{ARTISTS}", "w+") as artists:
                for arg in args.artists[0].upper():
                    categories = load_file_list(CATEGORIES)

                    #Find the matching URL for that category
                    for category_link in categories:
                        match = re.search(arg, category_link) 
                        if match is not None:
                            print(f"Scraping artists from: {category_link}", end="\r", flush=True)
                            soup = get_soup(category_link+ALL_LINKS_SUFFIX)
                            links = get_links(soup, ARTIST_ROUTE_REGEX)

                            #Save the results
                            for link in map(format_artist_link, links):
                                artists.write(link+"\n")
        except KeyboardInterrupt:
            print("\nManually interrupted. Quitting...")
            quit()
        print("\n--- SCRAPING ARTISTS FINISHED ---")


    #default; scrape all the artist categories
    elif args.allartists:
        print("--- SCRAPING ARTISTS ---")
        #operate on all the categories on the site
        try:
            with open(f"{ARTISTS}", "w+") as artists:
                for arg in f"0{uppercase}":
                    categories = load_file_list(CATEGORIES)

                    #Find the matching URL for that category
                    for category_link in categories:
                        match = re.search(arg, category_link) 
                        if match is not None:
                            print(f"Scraping artists from: {category_link}", end="\r", flush=True)
                            soup = get_soup(category_link+ALL_LINKS_SUFFIX)
                            links = get_links(soup, ARTIST_ROUTE_REGEX)

                            #Save the results
                            for link in map(format_artist_link, links):
                                artists.write(link+"\n")
        except KeyboardInterrupt:
            print("\nManually interrupted. Quitting...")
            quit()
        print("\n--- SCRAPING ARTISTS FINISHED ---")

    elif args.artisterrors:
        print("Need to handle errors")


#SONGS
    #TODO, run on the pi-cluster
    #TODO, scrape songs of a single artist, or of an entire category (A, B, etc)
    elif args.songs:  # scrape the song links from the artists' pages
        print("--- SCRAPING SONGS ---")
#         Path(SONGS).touch(exist_ok=True)
#         Path(ARTISTS_SCRAPED).touch(exist_ok=True)
        artists = set(load_file_list(ARTISTS))
        artists_scraped = set(load_file_list(ARTISTS_SCRAPED))
        artists_not_scraped = artists.difference(artists_scraped)
        print(f"Artists links not scraped: {len(artists_not_scraped)}")

        #open both files, close manually
        songs = open(SONGS, "a+")
        songs_scraped = open(SONGS_SCRAPED, "a+")
        artists_scraped = open(ARTISTS_SCRAPED, "a+")
        artist_errors = open(ARTIST_ERRORS, "a+")

        try: 
            for artist_url in artists_not_scraped:
                #For pretty terminal output
                length = len(artist_url)
                width = os.get_terminal_size().columns - length - 1
                print_this = f"{artist_url}{' ' * width}"
                print(print_this, end="\r", flush=True)

                soup = get_soup(artist_url)
                links = get_links(soup, LYRIC_ROUTE_REGEX)

                #Get artist name
                names = re.sub("https://www.lyrics.com/artist/", "", artist_url)
                names = names.split("/")

                #Ensure no extra slashes in name will confuse my naming scheme
                if len(names) > 2: 
                    artist_errors.write(artist_url+"\n")
                    continue
                else:
                    artist = unquote_plus(names[0])

                #Only allow dirs 0 and A-Z
                first_letter = artist[0]
                if first_letter not in letters:
                    artist_dir = "0"
                else:
                    artist_dir = artist[0].upper()

                #Ensure the artist's dir and file exists
                Path(f"{SUPPORT_DIR}{artist_dir}").mkdir(exist_ok=True)
                artist_file = f"{SUPPORT_DIR}{artist_dir}/{artist}.txt"
                Path(artist_file).touch(exist_ok=True)

                #Save the links for each artist in their own file
                with open(artist_file, "w+") as current_artist:
                    for link in map(format_song_link, links):
                        current_artist.write(link+"\n")

                        #Add the scraped song to the songs file
                        songs.write(link+"\n")

                #Keep track of the completed artist links
                artists_scraped.write(artist_url+"\n")

        except KeyboardInterrupt:
            print("\nManually interrupted. Quitting...")
            artists_scraped.close()
            songs.close()
            songs_scraped.close()
            quit()

        artists_scraped.close()
        songs.close()
        songs_scraped.close()
        print("\n--- SCRAPING SONGS FINISHED ---")


    elif args.songerrors:
        print("Need to handle song errors")


#LRYICS
    #TODO, this step needs to be run on the pi-cluster
    elif args.lyrics:
        print("--- SCRAPING LYRICS ---")
        songs = set(load_file_list(SONGS))
        lyrics_scraped = set(load_file_list(LYRICS_SCRAPED))
        lyrics_not_scraped = songs.difference(lyrics_scraped)
        print(f"Lyrics not scraped: {len(lyrics_not_scraped)}")

        #Open files
        lyrics_scraped = open(LYRICS_SCRAPED, "a+")
        lyrics_errors = open(LYRICS_ERRORS, "a+")

        for song_url in lyrics_not_scraped:
            #For pretty terminal output
            length = len(song_url)
            width = os.get_terminal_size().columns - length - 1
            print_this = f"{song_url}{' ' * width}"
            print(print_this, end="\r", flush=True)

            try:
                soup = get_soup(song_url)
                links = get_links(soup, LYRIC_ROUTE_REGEX)

                #Get names from url
                names = re.sub("https://www.lyrics.com/lyric/\d*/", "", song_url)
                names = names.split("/")
                artist = unquote_plus(names[0])
                song = unquote_plus(names[1])

                # If the name splitting is wierd, save the error for manual correction
                if len(names) > 2: 
                    lyrics_errors.write(song_url+"\n")
                    continue

                #Extract text
                lyrics = get_lyrics(soup)
                lyrics = list(lyrics.split("\n"))
#                 lyrics = list(map(lambda x: x.strip(), lyrics))
                #Added this to try and prevent the issue of stripping off the final "t"
                lyrics = list(map(lambda x: re.sub("\.txt", "", x), lyrics))

                #Save
                lyrics_scraped.write(song_url+"\n")
                data = f"{lyrics}".encode("utf8")

                #TODO, normalize names for the files here, I think the punctuation is affecting extraction later in the program
                info = tarfile.TarInfo(name=f"{artist}_{song}.txt")
                info.size = len(data)
                with tarfile.TarFile('lyrics.tar', 'a') as tar:
                    tar.addfile(info, io.BytesIO(data))
                lyrics_scraped.write(song_url+"\n")

            except KeyboardInterrupt:
                print("\nManually interrupted. Quitting....")
                lyrics_errors.write(song_url+"\n")
                lyrics_scraped.close()
                quit()
            except SSLEOFError: 
                print("\nSSL EOF Error. Quitting...")
                lyrics_errors.write(song_url+"\n")
                lyrics_scraped.close()
                quit()
            except MaxRetryError:
                print("\nMax Retry Error. Quitting...")
                lyrics_errors.write(song_url+"\n")
                lyrics_scraped.close()
                quit()
            except SSLError:
                print("\nRequest SSL Error. Quitting...")
                lyrics_errors.write(song_url+"\n")
                lyrics_scraped.close()
                quit()
            except:
                print("\nUnknown error. Quitting...")
                lyrics_errors.write(song_url+"\n")
                lyrics_scraped.close()
                quit()
        lyrics_scraped.close()
        lyrics_errors.close()

        print("--- SCRAPING LYRICS FINISHED ---")
