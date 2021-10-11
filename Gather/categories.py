"""Step 1: Gather the category links."""
# std lib
from pathlib import Path
import pickle
from pprint import pprint
import re
from typing import Any, List, Set, Text

#3rd party
from bs4 import BeautifulSoup, SoupStrainer, element
import requests


HOME_PAGE = "https://www.lyrics.com"
CATEGORY_ROUTE_REGEX = re.compile("^/artists/")
DATA_DIR = "../Databases/"
SLEEP_TIME = 3

def format_category_link(href: element.Tag) -> Text:
    """Formats URL for the artist. Returns String."""
    return f"{HOME_PAGE}{href.get('href')}"


def get_links(soup: BeautifulSoup, regex: re.Pattern) -> element.ResultSet:
    """Gets hrefs containing 'regex' from 'soup'."""
    return soup.find_all(href=regex)


def get_soup(link: Text) -> BeautifulSoup:
    """Gets soup from a link. Returns BeautifulSoup object."""
    request = persistent_request(link)
    return BeautifulSoup(request.content, "html.parser")


def persistent_request(link: Text) -> requests.models.Response:
    """Persistently makes a request. Returns HTTPresponse."""
    request = simple_request(link)
    if not request.status_code == 200:
        return three_requests(link)
    return request


def three_requests(link: Text) -> requests.models.Response:
    """Makes up to 3 request attempts. Returns HttpResponse."""
    errors = 0
    request = simple_request(link)
    while request.status_code != 200 and errors < 3:
        errors += 1
        sleep(SLEEP_TIME)
        request = simple_request(link)
        if request.status_code == 200:
            break
    return request


def get_href(tag: element.Tag):
    """Get the href attribute from the tag"""
    return CATEGORY_ROUTE_REGEX.search(tag.get("href"))


def load_pickle(file_name: str) -> list:
    f = open(f"../Databases/{file_name}.pickle", "rb")
    data = pickle.load(f)
    f.close()
    return data


def simple_request(link: Text) -> requests.models.Response:
    """Make an http request. Returns HttpResponse."""
    return requests.get(link)


def scrape_categories_from_home_page() -> Set[Text]:
    soup = get_soup(HOME_PAGE)
    category_links = get_links(soup, CATEGORY_ROUTE_REGEX)
    
    # get only the links that have /artists in the beginning
    category_links = list(filter(get_href, set(category_links)))

    # format useable URL
    category_links = [format_category_link(link) for link in category_links]
    category_links.sort()
    category_links = set(category_links)
    save_pickle("category_links", category_links)
    return category_links


if __name__ == "__main__":

    # scraped now
    category_links = scrape_categories_from_home_page()

    #load pickle
#     category_links = load_pickle("category_links")
#     category_links = list(category_links)
#     category_links.sort()
#     pprint(category_links[:10])
