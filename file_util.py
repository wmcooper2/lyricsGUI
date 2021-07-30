# std lib
from collections import namedtuple
import io
from pathlib import Path
from pprint import pprint
import re
import string
import tarfile
from typing import Any, Generator, List, TypeVar


tarData = TypeVar("tar", tarfile.TarFile, None)
match = TypeVar("match", re.match, None)
Song = namedtuple("Song", ["artist", "name"])


#TODO, continue writing tests from here
# def get_file_info(name: tarData) -> List[namedtuple]:
def all_songs_artists_and_names(tarball: tarData) -> List[namedtuple]:
    """Prepare list of songs' artists and names from tarball."""
    results = []
    #TODO refactor this out
    files = tar_contents(tarball)
    try:
        for file_ in enumerate(files):
#             print("file_.name:", file_[1].name)
#             print("file_:", file_)
            if file_[1].name.endswith(".txt"):
                artist_song = split_name(file_[1].name)
                if len(artist_song) > 2:
                    print("\nThere is more than one underscore.")
                    artist = input(f"What is the correct artist? {artist_song}: ")
                    song_name = input("What is the correct song? : ")
                else:
                    artist = artist_song[0].strip()
                    artist = re.sub("^block[0-9]{,3}/", "", artist)
                    song_name = artist_song[1].strip()
                entry = Song(artist, song_name)
                results.append(entry)
                print(f"Files parsed: {file_[0]}", end="\r", flush=True)
        print("\n")
    except KeyboardInterrupt:
        print("Manual interrupt. Quitting...")
        quit()
#     print("results:", results)
    return results


# def contents(file_: tarData) -> Generator[str, None, str]:
#     """Make a Generator of compressed tarfile."""
#     with tarfile.open(file_, "r:gz") as tar:
#         for thing in tar:
#             yield thing.name


#TODO, not easily testable
def divide_tarball(tarball: tarData, num: int) -> None:
    """Subdivide 'tarball' into 'num' tarballs.
        
        Will create 'num' new tarballs in current directory.
        Each tarball will have this format: "1.tar", "2.tar", etc.
    """
    #TODO, direct output tarballs to tars/ dir
    #   refactor to return something that can be saved outside of this function?
    #   not easily testable.

    print("Gathering archives...")
    #Member list
    main_tar = tarfile.open(tarball, "r")
    names = main_tar.getmembers()
    file_count = len(names)

    #Determine fair amount
    new_amount = file_count // num
    remainder = file_count % num

    #Divide the bulk of the archives
    name_counter = 0
    for file_ in range(1, num+1):
        name = f"tars/{str(file_)}.tar"
        new_tar = tarfile.open(name, mode="a:")

        #Put the new_amount of archives into the new tarball
        for new_file in range(new_amount):
            print(f"Subdividing the tarball: {name_counter}/{file_count}", end="\r", flush=True)
            archive_name = names[name_counter]
            name_counter += 1
            data = main_tar.extractfile(archive_name) 
            extracted = data.read()

            #add the extracted archive into the new tarball
            new_tar.addfile(archive_name, io.BytesIO(extracted))
        new_tar.close()

    #Divide the remainders
    for file_ in range(1, remainder+1):
        name = str(file_)+".tar"
        new_tar = tarfile.open(name, mode="a:")
        archive_name = names[name_counter]
        name_counter += 1
        data = main_tar.extractfile(archive_name) 
        extracted = data.read()

        #add the extracted archive into the new tarball
        new_tar.addfile(archive_name, io.BytesIO(extracted))
        new_tar.close()
    main_tar.close()
    print("Dividing archives finished.")


def extract_file_contents(file_name: str, name: tarData) -> bytes:
    """Get the archived file's contents."""
    with tarfile.open(name) as tar:
        data = tar.extractfile(file_name)
        return data.read().decode("utf-8")


def extract_file_contents_as_list(file_name: str, tarball: tarData) -> List[str]:
    """Get word list from uncompressed tarball."""
    with tarfile.open(tarball, "r") as tar:
        contents = tar.extractfile(file_name)
        data = contents.read()
        return data.decode("utf-8").split()


#TODO, continue writing tests from here
def get_tar_data(main_tar: List[str]) -> List[namedtuple]:
    """Add artist, song name and file path to DB."""
    print("main_tar: ", main_tar[0])
    results = []
#     counter = 0
    with tarfile.open(main_tar[0]) as tar:
        try:
            for file_ in enumerate(tar):
                artist_song = split_name(file_[1].name)
                if len(artist_song) > 2:
                    print("\nThere is more than one underscore.")
                    artist = input(f"What is the correct artist? {artist_song}: ")
                    song_name = input("What is the correct song? : ")
                else:
                    artist = artist_song[0].strip()
                    artist = re.sub("^block[0-9]{,3}/", "", artist)
                    song_name = artist_song[1].strip()
                entry = Song(artist, song_name)
                results.append(entry)
#                 counter += 1
#                 print(f"Files parsed: {counter}", end="\r", flush=True)
                print(f"Files parsed: {file_[0]}", end="\r", flush=True)
            print("\n")
        except KeyboardInterrupt:
            print("Manual interrupt. Quitting...")
            quit()
    return results


def lazy_word_list(name: tarData) -> Generator[List[str], None, None]:
    """Splits words into space delimited units. Yields List."""
    files = tar_contents(name)
    with tarfile.open(name, "r:gz") as tar:
        for file_ in files:
            data = tar.extractfile(file_).read().decode("utf-8")
            yield data.split()


def remove_all(char: str, list_: List[str]) -> List[str]:
    """Removes all char from list_."""
    while char in list_:
        list_.remove(char)
    return list_


def remove_all_digits(word: str) -> str:
    """Removes all digits from word."""
    for num in string.digits:
        word = remove_all(num, list(word))
    return "".join(word)


def remove_all_empty_elements(list_: List[Any]) -> List[Any]:
    """Removes all empty elements from list_."""
    while "" in list_:
        list_.remove("")
    return list_


def remove_all_punct(word: str) -> str:
    """Removes all punctuation from word."""
    for char in string.punctuation:
        word = remove_all(char, list(word))
    return "".join(word)


def make_tar_file(dir_: str, tarname: str) -> tarData:
    """Make the contents of dir_ into a tarball."""
    tar = tarfile.open(tarname, mode="a")
#     counter = 0
#     for f in Path(dir_).glob("*.txt"):
    for f in enumerate(Path(dir_).glob("*.txt")):
        tar.add(str(f[1]))
#         counter += 1
        print(f"Files added to tar: {f[0]}", end="\r", flush=True)
    tar.close()
    #TODO, return tar?, but it's closed, right? So, why?
    return tar


def search(pattern: str, file_: str) -> match:
    matches = 0
    counter = 0
    with tarfile.open(name=file_, mode="r") as tar:
        for file_ in tar:
            t = tar.getmember(file_.name)
            if t.isfile():
                try:
                    contents = extract_file_contents(t, file_)
                    res = re.search(pattern, str(contents))
                    if res != None:
                        print(f"{matches}/{counter}: {res}", end="\r", flush=True)
                        matches += 1
                    else:
                        print(f"{matches}/{counter}", end="\r", flush=True)
                except AttributeError:
                    print("Error: ", file_)
                except KeyboardInterrupt:
                    print("Manually quit.")
                    break

            #For testing
            if counter > 2:
                break
            counter += 1


def split_name(file_name: str) -> List[str]:
    """Separate the artist name from the song name."""
    name = re.sub(".txt", "", file_name)
    return name.split("_")


def tar_contents(file_: tarData) -> Generator[str, None, str]:
    """Make a Generator of the tarfile."""
    with tarfile.open(name=file_, mode="r", ignore_zeros=True) as tar:
        yield tar.next()


def word_list(list_: str) -> List[str]:
    """Load word list."""
    with open(list_, "r") as f:
        return f.readlines()


# if __name__ == "__main__":
#     divide_tarball("testing_uncompressed.tar", 5)
#     divide_tarball("testing_uncompressed.tar", 7)
#     divide_tarball("combined.tar", 16)
