"""Step 3: Gather the song links."""
# stand lib
import concurrent.futures
import logging
from pathlib import Path
import pickle
from pprint import pprint
import re
import time
from typing import List, Set, Text

# 3rd party
from bs4 import BeautifulSoup, SoupStrainer, element

# custom
import categories
from util import (
    count_artists,
    count_unique_lines,
    format_artist_link,
    get_links,
    get_soup,
    progress_bar,
    scrape_setup)

HOME_PAGE = "https://www.lyrics.com"

def timing(function):
    """Timing decorator."""
    def wrapper(*args, **kwargs):
        start = time.time()
        function(*args, **kwargs)
        end = time.time()
        print("time taken:", end - start)
    return wrapper


def format_category_link(href: element.Tag) -> Text:
    """Formats URL for the artist. Returns String."""
    return f"{HOME_PAGE}{href.get('href')}"


def load_pickle(file_name: Text) -> list:
    try:
        f = open(f"../Databases/{file_name}.pickle", "rb")
        data = pickle.load(f)
        f.close()
        return data
    except:
        return []


def save_pickle(file_name: Text, data: Set[Text]) -> None:
    f = open(f"../Databases/{file_name}.pickle", "wb+")
    pickle.dump(data, f)
    f.close()


# def scrape_song_links_from_artist_links(artist_links: Set[Text]) -> Set[Text]:
def scrape_song_links_from_artist_links(artist_url: Text) -> Set[Text]:
    """Main scraping function. Returns set of song links."""
#     total = len(artist_links)
    pattern = re.compile("^/lyric/")
#     song_links = set()
#     for index, artist_url in enumerate(artist_links, start=1):
    soup = get_soup(artist_url)
    links = set(get_links(soup, pattern))
    links = [format_category_link(link) for link in links]
#         pprint(links)
#     print(artist_url, len(links))
#     song_links.update(set(links))
#         quit()
#         progress_bar(index, total)

#     for every 100 artists, save song_links to the pickle, then reload the pickle
#         if index % 100 == 0:
#             save_pickle("song_links", song_links)

    # save it one last time
#     save_pickle("song_links", song_links)
    return set(links)


@timing
def thread_manager(artist_links: Set[Text]) -> Set[Text]:
    #load existing song pickle
    song_links = set(load_pickle("song_links"))

    total = len(artist_links)
    progress = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(scrape_song_links_from_artist_links, link) for link in artist_links if link not in artist_links_already_scraped}
        for future in concurrent.futures.as_completed(futures, timeout=5):
            result = None
            try:
                result = future.result()
            except TypeError as e:
                logging.debug(f"TypeError: {link}")
            if result:
                song_links.update(result)

            progress += 1
            print("Progress:", progress, end="\r")

            # partial save point
            if progress % 100 == 0:
                save_pickle("song_links", song_links)
    save_pickle("song_links", song_links)
    return song_links


if __name__ == "__main__":
    logging.basicConfig(filename="../Logs/gather_songs.errors", encoding="utf-8", level=logging.DEBUG)

    #all the artist links
    artist_links = set(load_pickle("artist_links"))
    print(f"artist_links: {len(artist_links)}")

    #load artist links already scraped
    artist_links_already_scraped = set(load_pickle("artist_links_already_scraped"))
    print(f"artist_links_already_scraped: {len(artist_links_already_scraped)}")

    #filter the ones that need to be scraped
    artist_links = artist_links.difference(artist_links_already_scraped)
    artist_links = list(artist_links)
    artist_links.sort()
    print(f"artist_links: {len(artist_links)}")

    # scrape now
    start = 0
    end = 2000
    song_links = thread_manager(artist_links[start:end])

    # save the scraped work so you don't scrape again
    artist_links_already_scraped.update(set(artist_links[start:end]))
    save_pickle("artist_links_already_scraped", artist_links_already_scraped)
    
    #show example of what was scraped
#     song_links = list(song_links)
#     song_links.sort()
#     pprint(song_links[:10])


    #load pickle
#     artist_links = load_pickle("artist_links")
#     song_links = list(song_links)
#     song_links.sort()
#     pprint(song_links[:10])
