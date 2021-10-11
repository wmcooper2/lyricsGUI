#std lib
import re

#3rd party
import bs4
import pytest
import requests

#custom
from Gather import categories


class TestGatherCategories:

    @pytest.fixture
    def home_page(self):
        return "https://www.lyrics.com"

    @pytest.fixture
    def soup(self, home_page):
        return categories.get_soup(home_page)

    @pytest.fixture
    def search_string(self):
        return "^/artists/"

    @pytest.fixture
    def artist_search_regex(self, search_string):
        return re.compile(search_string)

    @pytest.fixture
    def artist_category_tag(self):
        #TODO, convert to tage element
        soup = bs4.BeautifulSoup('<a href="/artists/U">U</a>', "html.parser")
        return soup.a

    def test_format_category_link(self, artist_category_tag):
        result = categories.format_category_link(artist_category_tag)
        assert result == "https://www.lyrics.com/artists/U"

    def test_get_soup_is_soup_instance(self, home_page):
        assert isinstance(categories.get_soup(home_page), bs4.BeautifulSoup)

    def test_get_links(self, soup, artist_search_regex):
        links = categories.get_links(soup, artist_search_regex)
        assert isinstance(links, list)
        assert len(links) > 0



# def test_get_href():
#     categories.get_href()
