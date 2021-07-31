# 3rd party
import pytest
from bs4 import BeautifulSoup, element

# custom
from constants import HOME_PAGE, CATEGORY_ROUTE, LINK_STRING_TEST, LINE_COUNT_TEST
from scrapeutil import (
    count_unique_lines,
#     count_lines,
    get_soup,
    get_links,
    simple_request,
    persistent_request,
    load_file_list)

def test_simple_request():
    assert simple_request(HOME_PAGE).status_code == 200

# def test_three_requests()

def test_persistent_request():
    assert persistent_request(HOME_PAGE).status_code == 200

def test_get_links():
    soup = get_soup(HOME_PAGE)
    assert type(get_links(soup, LINK_STRING_TEST)) == element.ResultSet

def test_get_soup():
    assert type(get_soup(HOME_PAGE)) == BeautifulSoup
    
# def test_save_list():

# def test_save_json():

# def test_load_json():

# def test_count_unique_lines():
#     assert count_unique_lines(LINE_COUNT_TEST) == 5

# def test_count_lines():
#     assert count_lines(LINE_COUNT_TEST) == 6

# def test_write_to_file():

# def test_load_file_list():
#     assert type(load_file_list(LINE_COUNT_TEST)) is list
#     assert len(load_file_list(LINE_COUNT_TEST)) == 6

# def test_count_songs():

# def test_count_files():

# def test_count_files():

# def test_buttontest():




# def test_category_link_directs_to_proper_site():
#     assert # category link request returns 200
#     assert # the link address for category I is "http://www.lyrics.com/artists/I"
#     pass

