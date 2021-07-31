# std lib
import re
from typing import List, Text

# 3rd party
from bs4 import BeautifulSoup, SoupStrainer, element

#custom
from tvconstants import HOME_PAGE


def format_tv_category_link(href: element.Tag) -> Text:
    """Formats URL for the tv_category. Returns String."""
    return f"{HOME_PAGE}{href.get('href')}"


def tv_show_main_page_hrefs(soup: BeautifulSoup, regex: re.Pattern,) -> List[str]:
    """Get list of hrefs for scripts' main pages."""
    return soup.find_all(href=regex)
