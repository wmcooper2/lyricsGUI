#!/usr/bin/env python3.7
# scrapeartists.py
"""Scrapes artist links. Step 2."""

# stand lib
from pathlib import Path
from pprint import pprint

# custom
from constants import (
    ARTIST_DIR,
    CATEGORY_FIN,
    ARTIST_ERRORS,
    ARTIST_FIN)
from scrapeutil import (
    count_artists,
    count_unique_lines,
    format_artist_link,
    get_links,
    get_soup,
    progress_bar,
    save,
    scrape_setup)


def scrape() -> None:
    """Main scraping function. Returns None."""
    print("--- ARTIST SCRAPING STARTED ---")
    errors = []
    todo, finished = scrape_setup(CATEGORY_FIN, ARTIST_FIN)
    total = len(todo)
    completed = 0

    for cat in todo:
        try:
            soup = get_soup(cat)
            art_hrefs = get_links(soup, "^artist")
            art_links = list(map(format_artist_link, art_hrefs))
            category = Path(cat).parts[3]
            text_file = (ARTIST_DIR + category + "_" 
                         + "artistlinks.txt") 
            save(art_links, text_file)
            finished.append(cat)
        except:
            errors.append(cat)
        completed += 1
        progress_bar(completed, total)
    save(errors, ARTIST_ERRORS)
    save(finished, ARTIST_FIN)
    print("--- ARTIST SCRAPING FINISHED ---")

# if __name__ == "__main__":
#     scrape()
