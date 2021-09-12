#!/usr/bin/env python3.7
# scrapeutil.py
"""Utility module Lyric Scraper program."""

# stand lib
import json
from pathlib import Path
import re
import subprocess as sp
from time import sleep
from typing import (
    Any,
    List,
    Set,
    Text,
    Tuple)
from urllib.parse import unquote_plus

# 3rd party
from bs4 import BeautifulSoup, SoupStrainer, element
import requests

# custom
from constants import (
    HOME_PAGE,
    PUNCTUATION,
    SLEEP_TIME,
    SONGS)

filter_ = SoupStrainer("a")


def buttontest() -> None:
    """Print test message. Returns None."""
    print("Button works")
    return None


def count_artists(dir_: Text) -> int:
    """Counts unique artist links. Returns Integer."""
    total = 0
    for x in Path(dir_).iterdir():
        if str(x).endswith("txt"):
            total += count_unique_lines(str(x))
    return total


# def count_lines(file_: Text, msg: Text = None) -> int:
def count_lines(file_: Text) -> int:
    """Counts lines in 'file_'. Returns Integer."""
    count = 0
    with open(file_, "r") as f:
        for line in f.readlines():
            count += 1
#             print('\r%s %s' % (msg, count), end='\r')
#     print()
    return count


def count_unique_lines(file_: Text) -> int:
    """Counts unique lines in 'file_'. Returns Integer."""
    with open(file_, "r") as f:
        return len(set(f.readlines()))


def get_artist(soup: BeautifulSoup) -> Text:
    """Extracts the artist's name."""
    name_element = soup.h3.a
    return name_element.get_text()


def get_links(soup: BeautifulSoup, string: Text) -> element.ResultSet:
    """Gets hrefs containing 'string' from 'soup'."""
    return soup.find_all(href=re.compile(string))


def get_lyrics(soup: BeautifulSoup) -> Text:
    """Extract the lyrics from 'soup'."""
    lyric_body = soup.find(id="lyric-body-text")
    return lyric_body.get_text()


#TODO, change Any to str and ...?
# def get_hrefs(string: Text) -> Any:
# def get_hrefs(hrefs: Set[Any]) -> Any:
def get_hrefs(hrefs: Set[element.Tag]) -> Any:
    """Gets hrefs. Returns List."""
    return hrefs.find_all(href=re.compile(hrefs))


def get_song(soup: BeautifulSoup) -> Text:
    """Extracts the song's name. Returns String."""
    name_element = soup.find(id="lyric-title-text")
    return remove_slash(name_element.get_text())


#TODO, change Any to ...?
def get_soup(link: Text, filter_: Any = None) -> BeautifulSoup:
    """Gets soup from a link. Returns BeautifulSoup object."""
    request = persistent_request(link)
    return BeautifulSoup(request.content, "html.parser", parse_only=filter_)


def ensure_exists(string: Text) -> None:
    """Makes 'string' dir if doesn't exist. Returns None."""
    if not Path(string).exists():
        Path(string).mkdir()
    return None


def ensure_file_exists(string: Text) -> None:
    """Makes 'string' dir if doesn't exist. Returns None."""
    if not Path(string).exists():
        Path(string).touch()
    return None

 
def file_gen(file_: Text) -> Any:
    """Make a generator of a text file. Returns Generator."""
    with open(SONGS) as song_list:
        for link in song_list.readlines():
            yield link.strip()


def format_category_link(href: element.Tag) -> Text:
    """Formats URL for the artist. Returns String."""
    return f"{HOME_PAGE}{href.get('href')}"


def format_artist_link(href: element.Tag) -> Text:
    """Formats URL for the artist. Returns String."""
    return f"{HOME_PAGE}/{href.get('href')}"


def format_song_link(href: element.Tag) -> Text:
    """Formats URL for the artist. Returns String."""
    return f"{HOME_PAGE}{href.get('href')}"


def format_artist_name(name: Text) -> Text:
    """Formats the artist's name. Returns String."""
    return unquote_plus(name)
#     artist = unquote(name)
#     artist = artist.replace("+", " ")
#     return artist.replace("/", " ")



def format_file_name(artist: Text, song: Text) -> Text:
    """Assembles basic file name. Returns String."""
    return artist + "_" + song + ".txt"


#TODO, find what this change affects
def format_song_name(href: element.Tag) -> Text:
    """Formats the song's name. Returns String."""
    song = unquote_plus(Path(href.get("href")).parts[4])
#     song = song.replace("+", " ")
#     song = song.replace("-", " ")
    return song


def load_categories(paths: Text) -> List[Text]:
    """Loads artists file names. Returns List."""
    temp = []
    for file_ in Path(paths).iterdir():
        temp.append(str(file_))
    temp.sort() 
    return temp


def load_file_list(file_: str, msg: str = None) -> List[str]:
    """Loads 'file_'. Returns List."""
    temp = []
#     total = count_lines(file_, msg)
    total = count_lines(file_)
    loaded = 0
    with open(file_, "r") as f:
        for line in f.readlines():
            temp.append(line.strip())
            loaded += 1
    return temp


#TODO, change Any to json type
def load_json(file_path: Text) -> Any:
    """Loads a json file. Returns Json object."""
    with open(file_path) as file_obj:
        artist_list = json.loads(file_obj.read())
    return artist_list 


#TODO
# def manually_correct_lyric_errors():
#     print("Song name parsing error:", names)
#         song_name = input("What is the song's name? ")
#     else:
#         song_name = unquote_plus(names[1])
#     print("song_name:", song_name)
#     pass


# def persistent_request(link: Text) -> Any:
def persistent_request(link: Text) -> requests.models.Response:
#     """Persistently makes a request. Returns Request object."""
    """Persistently makes a request. Returns HTTPresponse."""
    request = simple_request(link)
    if not request.status_code == 200:
        return three_requests(link)
    return request


def progress_bar(iteration: int,
                 total: int,
                 prefix: Text = 'Todo:',
                 suffix: Text = '',
                 decimals: int = 1,
                 length: int = 100,
                 fill: Text = '█') -> None:
    """
    Call in a loop to create terminal progress bar. Returns None.
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration is total: 
        print()
    return None


def remove_punctuation(name: Text) -> Text:
    """Removes punctuation from song. Returns String."""
    no_punct = []
    for character in name:
        if character not in PUNCTUATION:
            no_punct.append(character)
    return ''.join(no_punct)


def remove_slash(string: Text) -> Text:
    """Removes the forward slash. Returns String."""
    temp = []
    for c in string:
        if c != "/":
#         if c is not "/":
            temp.append(c)
    return "".join(temp)


def save(list_: List[Text], location: Text) -> None:
    """Writes 'list_' to 'location' as txt file. Returns None."""
    with open(location, "w+") as f:
        for element in sorted(list_):
            f.write(element+"\n")
    return None


def save_append(list_: Text, location: Text) -> None:
    """Appends 'list_' to 'location' as txt file. Returns None."""
    with open(location, "a+") as f:
        for element in list_:
            f.write(element+"\n")
    return None


def save_append_line(string: Text, location: Text) -> None:
    """Appends 'string' to location's text file. Returns None."""
    with open(location, "a+") as f:
        f.write(string+"\n")
    return None


def save_json(json_obj: Text, file_name: Text) -> None:
    """Saves 'json_obj' to 'file_name'. Returns None."""
    dumping = json.dumps(json_obj, sort_keys=True, indent=4)
    with open(file_name, "a+") as file_obj:
        file_obj.write(dumping)
    return None


def save_lyrics(list_: List[Text], location: Text) -> None:
    """Writes 'list_' to 'location' as txt file. Returns None."""
    with open(location, "w+") as f:
        for element in list_:
            f.write(element+"\n")
    return None


# def scrape_setup(cur_todo: Text, cur_fin: Text) -> Tuple[List[Text], List[Text]]:
def scrape_setup(cur_todo: Text, cur_fin: Text) -> [List[Text], List[Text]]:
    """Determines which links need to be scraped. 
        needs;
            - current todo file
            - current stage finished file
        Returns 2 Lists."""
#     todo = set(load_file_list(cur_todo, "To do:"))
#     finished = set(load_file_list(cur_fin, "Finished:"))
    todo = set(load_file_list(cur_todo))
    finished = set(load_file_list(cur_fin))
#     todo_len = len(todo)
#     finished_len = len(finished)
#     completed = 0
    diff = todo.difference(finished)
#     print("Unique todos:", len(diff))
#     return (list(diff), list(finished))
    return list(diff), list(finished)

def scrape_setup_song(prev_stage_dir: Text,
                      cur_fin: Text) -> Tuple[List[Text], List[Text]]:
    """Determines which links need to be scraped. 
        needs;
            - current todo file
            - current stage finished file. 
        Returns 2 Lists."""
    prev_fin = []
    for file_ in Path(prev_stage_dir).iterdir():
        prev_fin += load_file_list(str(file_))
    prev_fin = set(prev_fin)
    finished = set(load_file_list(cur_fin))
    return (list(prev_fin.difference(finished)), list(finished))


# def simple_request(link: Text) -> Any:
def simple_request(link: Text) -> requests.models.Response:
    """Make an http request. Returns HttpResponse."""
    return requests.get(link)


# def three_requests(link: Text) -> Any:
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
