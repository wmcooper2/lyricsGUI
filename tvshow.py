# std lib
import argparse
from pprint import pprint
import re

# custom
from scrapeutil import get_soup, get_links
from tvshow_util import format_tv_category_link, tv_show_main_page_hrefs
from tvconstants import (
    CATEGORIES,
    CATEGORY_ROUTE_REGEX,
    HOME_PAGE,
    SCRIPT_ROUTE_REGEX,
    TV_SHOW_DESC)


if __name__ == "__main__":

    #Load description
    with open(TV_SHOW_DESC) as f:
        how_to_use = f.read()
    
    parser = argparse.ArgumentParser(prog="TV Show Test Scraper", formatter_class=argparse.RawDescriptionHelpFormatter, description=how_to_use)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--categories", action="store_true", help="Scrape categories from IMSDB.com")
    group.add_argument("--scriptlinks", action="store_true", help="Scrape main page links from IMSDB.com")

    args = parser.parse_args()

#CATEGORIES
    if args.categories: 
        print("--- SCRAPING TV CATEGORIES ---")
        soup = get_soup(HOME_PAGE)
        links = get_links(soup, CATEGORY_ROUTE_REGEX)
        print(f"A-tag example: {links[1]}")  # show example
        print(f"Saved URL example: {format_tv_category_link(links[1])}")  # show example
        with open(CATEGORIES, "w+") as categories:
            for link in map(format_tv_category_link, links):
                categories.write(link+"\n")
        print("--- SCRAPING TV CATEGORIES FINISHED ---")

#SCRIPTLINKS
    elif args.scriptlinks:
        print("--- SCRAPING TV MAIN PAGE LINKS ---")
        pattern = re.compile(SCRIPT_ROUTE_REGEX)
        print("pattern:", pattern)

        with open(CATEGORIES, "r") as f:
            for show in f.readlines():
                soup = get_soup(show.strip())
                atags = soup.find_all("a")
#                 print("len atags:", len(atags))

                #extract all the Movie Script lines
                for tag in atags:
                    href = tag.attrs["href"]
#                     print("tag:", tag)

                    #!!! tag is a bs4.element.tag object, cast to str
                    results = re.search(pattern, str(tag))
                    print("results:", results)

        print("--- SCRAPING TV MAIN PAGE LINKS FINISHED---")
