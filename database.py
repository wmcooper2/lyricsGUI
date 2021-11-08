#std lib
from collections import namedtuple
import difflib
import logging
from pprint import pprint
import re
import sqlite3
from typing import Any, Callable, Generator, List, Optional, Set, Text, Tuple

#custom
# import parse_urls as urlparser

DATABASE = "Databases/lyrics.db"
DBRecord = namedtuple("DBRecord", ["id", "artist", "song", "lyrics"])

# csv.field_size_limit(sys.maxsize)  # Increase field size limit

def list_print(list_: List[Any]):
    for element in list_: 
        print(element)
        print()

#subclass sqlite?
class Database():

    def __init__(self) -> None:
        self.con, self.cur = self.con_cur()

    def __str__(self):
        return "Lyrics database"

    def __exit__(self):
        self.con.close()
        self.cur.close()

    def con_cur(self) -> Tuple[sqlite3.Cursor, sqlite3.Connection]:
        """Get cursor and connection object from DB."""
        
        con = sqlite3.connect("Databases/lyrics.db")
        cur = con.cursor()
        return con, cur

    def all_records_threaded(self) -> Optional[Set[DBRecord]]:
        con, cur = self.con_cur()
        cur.execute(f"SELECT * FROM songs")
        records = cur.fetchall()
        cur.close()
        con.close()
        for record in records:
            yield DBRecord(record[0], record[1], record[2], record[3])
        return records


    def artist(self, artist: Text) -> Optional[DBRecord]:
        """Get records of a single artist."""
        return self.songs_from_artist(artist)


    #TODO: return DBRecords with None in the song field (for consistency)
    def artists(self) -> List[Tuple[Text]]:
        """Get all artists in database."""

        self.cur.execute(f"SELECT DISTINCT artist FROM songs")
        result = self.cur.fetchall()
        return result


    def artist_and_song(self, artist: Text, song: Text) -> DBRecord:
        """Returns a single element list of 'song' by 'artist'."""

        self.cur.execute(f"SELECT * FROM songs WHERE artist=? AND song=?", (artist, song))
        results = self.cur.fetchall()
        try:
            results = results[0]
        except IndexError:
            results = None
        if results:
            return DBRecord(results[0], results[1], results[2], results[3])
        else:
            return DBRecord("", "", "", "")


    def index_search(self, index: int, step: int) -> List:
        """Search for records starting at 'index'."""

        self.cur.execute(f"SELECT * FROM songs WHERE id>=? AND id<=?", (index, index+step))
        records = self.cur.fetchall()
        return records


    #TODO: rename to be more flexible with the debug choice at the top of this module
    def populate_db_with_demo_data(self) -> None:
        """Inserts about 60000 songs into the database"""

        counter = 0
        with open(f"Databases/{DB}.csv", "r") as f:
            data = csv.reader(f, delimiter="|")
            for row in data:
                row = [counter] + row
                self.cur.execute("""INSERT INTO {TABLE} VALUES(?, ?, ?, ?)""", row)
                counter += 1
                print(counter, end="\r")


    def songs_from_artist(self, artist: Text) -> List[DBRecord]:
        """Get all songs from 'artist'."""
        
        self.cur.execute(f"SELECT * FROM songs WHERE artist=?", (artist,))
        results = self.cur.fetchall()
        results = [DBRecord(result[0], result[1], result[2], result[3]) for result in results]
        return results


    def artists_having_song(self, song: Text) -> List[DBRecord]:
        """Get all artists who have a song with the same name."""
        
        self.cur.execute(f"SELECT * FROM songs WHERE song=?", (song,))
        results = self.cur.fetchall()
        results = [DBRecord(result[0], result[1], result[2], result[3]) for result in results]
        return results


    #TODO, test
    def mp_record_check(self, artist: Text, song: Text) -> bool:
        """Checks if a record exists in the database """

        self.cur.execute(f"SELECT artist FROM {TABLE} WHERE artist=? AND song=?", (artist, song))
        results = self.cur.fetchall()
        return bool(results)


    #TODO, test
    def all_records(self) -> Generator:
        """Get all records."""

        con, cur = self.con_cur()
        cur.execute(f"SELECT * FROM songs")
        records = cur.fetchall()
        for record in records:
            yield DBRecord(record[0], record[1], record[2], record[3])
        return records


    def record_check(self, artist: Text, song: Text, cur: sqlite3.Cursor) -> bool:
        """Checks if a record exists in the database """

        cur.execute(f"SELECT artist FROM songs WHERE artist=? AND song=?", (artist, song))
        results = cur.fetchall()
        cur.close()
        return bool(results)


    def record_count(self) -> int:
        """Get record count in DB."""

        self.cur.execute("SELECT COUNT(*) FROM songs")
        result = self.cur.fetchall()[0][0]
        return result


class FuzzyDatabase(Database):

    def __init__(self) -> None:
        self.con, self.cur = self.con_cur()

    def __str__(self):
        return "Fuzzy lyrics database"

    def __exit__(self):
        self.con.close()
        self.cur.close()


    def fuzzy_songs_from_artist(self, artist: Text) -> List[DBRecord]:
        """Fuzzy search of songs from 'artist'."""

        #get all artists
        self.cur.execute("SELECT DISTINCT(artist) FROM songs")
        results = self.cur.fetchall()

        #convert from List[Tuple] to List[Text]
        results = [result[0] for result in results]

        #choose most likely artists
        possible_matches = difflib.get_close_matches(artist, results)

        #make set
        possible_matches = set(possible_matches)
        possible_matches = list(possible_matches)

        # perform db search using the top closest matches
        results = list()
        for match in possible_matches:
            results.append(self.songs_from_artist(match))

        final = [nested for result in results for nested in result]
        if final:
            return [DBRecord(record[0], record[1], record[2], record[3]) for record in final]
        else:
            return [DBRecord("", "", "", "")]

        #TODO display records in gui


    #done
    def fuzzy_artist_and_song(self, artist: Text, song: Text) -> DBRecord:
        """Fuzzy search for a 'song' by an 'artist'."""

        #fuzzy search for artists
        artist_records = set(self.fuzzy_artist(artist))

        #fuzzy search for songs
        song_records = set(self.fuzzy_song(song))

        #find what's in both sets
        likely_matches = artist_records.intersection(song_records)
        matches = list(likely_matches)

        if matches:
            return [DBRecord(match[0], match[1], match[2], match[3]) for match in matches]
        else:
            return [DBRecord("", "", "", "")]
 

    #done
    def fuzzy_artist(self, artist: Text) -> List[DBRecord]:
        """Fuzzy search for 'artist'. Returns list of artists and the song."""

        self.cur.execute("SELECT artist FROM songs")
        records = self.cur.fetchall()
        records = [record[0] for record in records]

        # get closest match from all of them
        possible_matches = difflib.get_close_matches(artist, records)
        possible_matches = set(possible_matches)
        possible_matches = list(possible_matches)

        # perform db search using the top closest matches
        results = list()
        for match in possible_matches:
            results.append(self.artist(match))

        #flatten the list
        final = [nested for result in results for nested in result]
        if final:
            return [DBRecord(record[0], record[1], record[2], record[3]) for record in final]
        else:
            return [DBRecord("", "", "", "")]

 
    #done
    def fuzzy_song(self, song: Text) -> List[DBRecord]:
        """Fuzzy search for 'song'. Returns list of artists and the song."""

        self.cur.execute("SELECT song FROM songs")
        records = self.cur.fetchall()
        records = [record[0] for record in records]

        # get closest match from all of them
        possible_matches = difflib.get_close_matches(song, records)
        possible_matches = set(possible_matches)
        possible_matches = list(possible_matches)

        # perform db search using the top closest matches
        results = list()
        for match in possible_matches:
            results.append(self.artists_having_song(match))

        #flatten the list
        final = [nested for result in results for nested in result]
        if final:
            return [DBRecord(record[0], record[1], record[2], record[3]) for record in final]
        else:
            return [DBRecord("", "", "", "")]




################################################################################
#   Shared Functions
################################################################################
def lyrics_db():
    """Get connection and cursor to DB."""

    con = sqlite3.Connection(DATABASE)
    cur = con.cursor()
    return cur, con


def _save(con: sqlite3.Connection) -> None:
    """Save the changes made to the DB."""

    con.commit()


def close_connection(cur: sqlite3.Cursor, con: sqlite3.Connection) -> None:
    """Close the DB."""

    _save(con)
    cur.close()
    con.close()


def init_db_table(cur: sqlite3.Cursor) -> None:
    """Initialize the DB table."""

    cur.execute(f"CREATE TABLE IF NOT EXISTS {TABLE}(id INTEGER PRIMARY KEY AUTOINCREMENT, artist TEXT NOT NULL, song TEXT NOT NULL, lyrics TEXT NOT NULL)")


def get_highest_db_index(cur: sqlite3.Cursor, table: Text) -> int:
    """Get the highest DB index."""

    sql_statement = f"SELECT MAX(id) FROM {table}"
    result = cur.execute(sql_statement)
    result = result.fetchall()
    return result[0][0]


def all_file_records_in_db():
    """Get all DB records."""

    file_records = "Databases/file_records.pickle"
    records = urlparser.load_pickle(file_records)
    for index, record in enumerate(records, start=1):
        lyrics = artist_and_song(record.artist, record.song)
        if not lyrics:
            logging.debug(f"Record not found in DB: {record}")


if __name__ == "__main__":
    base_name = "db_health"
    logging.basicConfig(filename=f"Logs/{base_name}.errors", encoding="utf-8", level=logging.DEBUG)

    db = FuzzyDatabase()
#     db.fuzzy_song("call in he familt")
    list_print(db.fuzzy_songs_from_artist("the police"))
