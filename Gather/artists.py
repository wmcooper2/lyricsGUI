"""Step 2: Gather the artist links."""
# stand lib
import logging
from pathlib import Path
import pickle
from pprint import pprint
import re
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


def format_category_link(href: element.Tag) -> Text:
    """Formats URL for the artist. Returns String."""
    return f"{HOME_PAGE}/{href.get('href')}"


def get_links(soup: BeautifulSoup, pattern: re.Pattern) -> element.ResultSet:
    """Gets hrefs containing 'string' from 'soup'."""
    return soup.find_all(href=pattern)


def load_pickle(file_name: Text) -> list:
    f = open(f"../Databases/{file_name}.pickle", "rb")
    data = pickle.load(f)
    f.close()
    return data


def save_pickle(file_name: Text, data: Set[Text]) -> None:
    f = open(f"../Databases/{file_name}.pickle", "wb+")
    pickle.dump(data, f)
    f.close()

def scrape_artist_links_from_category_links(category_links: List[Text]) -> Set[Text]:
    """Main scraping function. Returns list of artist urls."""
    total = len(category_links)
    pattern = re.compile("^artist/")
    artist_links = set()
    for index, category in enumerate(category_links, start=1):
        soup = get_soup(f"{category}/99999") # the whole list of artists
        links = set(get_links(soup, pattern))
        links = [format_category_link(link) for link in links]
        artist_links.update(set(links))
        progress_bar(index, total)
    save_pickle("artist_links", artist_links)
    return artist_links

if __name__ == "__main__":
    logging.basicConfig(filename="../Logs/gather_artists.errors", encoding="utf-8", level=logging.DEBUG)

    # scraped now
    category_links = load_pickle("category_links")
    artist_links = scrape_artist_links_from_category_links(category_links)
    artist_links = list(artist_links)
    artist_links.sort()
    pprint(artist_links[:10])

    #load pickle
#     artist_links = load_pickle("artist_links")
#     artist_links = list(artist_links)
#     artist_links.sort()
#     pprint(artist_links[:10])
