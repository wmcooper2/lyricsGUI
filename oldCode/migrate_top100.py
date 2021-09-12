from db_util import db_connect


def save_incomplete_artists_or_songs():
    """Save records where artist or song field is blank."""
    db, connection = db_connect("top100.db")
    cursor = connection.execute("select * from rankings where artist='' or song=''");
    results = cursor.fetchall()
    with open("support/bad_records_top_100.txt", "w+") as f:
        for result in results:
            f.write(str(result))
            f.write("\n")
#     print("results:", len(results))
    connection.close()


def save_list_of_unique_artists():
    """Save a list of unique artist field names.
        
        Some artist names are duplicated because records may contain such variations as;
            - tobyMac Featuring Beckah Shae & Siti Monroe
            - tobyMac Featuring Blanca
            - tobyMac Featuring Capital Kings
            - Toby Keith
            - Toby Keith & Sammy Hagar

        Also, "toby" is different than "Toby"
    """

    #get list of unique artists in the db
    db, connection = db_connect("top100.db")
    cursor = connection.execute("select * from rankings");
    results = cursor.fetchall()

    unique_artists = set()
    for result in results:
        unique_artists.add(result[1])
    artists = sorted(list(unique_artists))
    artists.remove("")

    with open("support/unique_artists_top_100.txt", "w+") as f:
        for artist in artists:
            f.write(artist+"\n")
    print("artists:", len(artists))
    print("artists:", artists[:10])
    connection.close()


def save_list_of_unique_songs():
    """Save a list of unique song field names.
        
        Many song names contain 'strange' characters like;
            "'*+÷-=<!?¿#$&@.…{(
    """

    #get list of unique songs in the db
    db, connection = db_connect("top100.db")
    cursor = connection.execute("select * from rankings");
    results = cursor.fetchall()

    unique_songs = set()
    for result in results:
        unique_songs.add(result[2])
    songs = sorted(list(unique_songs))
    songs.remove("")

    with open("support/unique_songs_top_100.txt", "w+") as f:
        for artist in songs:
            f.write(artist+"\n")
    print("songs:", len(songs))
    print("songs:", songs[:10])
    connection.close()


def save_list_of_unique_dates():
    """Save a list of unique date field names."""

    #get list of unique songs in the db
    db, connection = db_connect("top100.db")
    cursor = connection.execute("select * from rankings");
    results = cursor.fetchall()

    unique_dates = set()
    for result in results:
        unique_dates.add(result[3])
    dates = sorted(list(unique_dates))

    with open("support/unique_dates_top_100.txt", "w+") as f:
        for date in dates:
            f.write(date+"\n")
    print("dates:", len(dates))
    print("dates:", dates[:10])
    connection.close()
save_list_of_unique_dates()
