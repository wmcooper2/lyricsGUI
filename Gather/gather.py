"""Lyrics.com scraper"""
# std lib
from pprint import pprint

#custom
from Gather.categories import scrape_categories_from_home_page

if __name__ == "__main__":
    category_links = scrape_categories_from_home_page()
    pprint(category_links)

