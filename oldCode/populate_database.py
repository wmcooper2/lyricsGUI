from db_util import populate_database, create_db

if __name__ == "__main__":

    #Testing DB population
    tarname = "2.tar.gz"
    results = populate_database(tarname)


    #Populate the database with the basics
#     for x in range(1, 5):
#         tarname = f"{str(x)}.tar.gz"
#         results = populate_database(tarname)


    #Save and close DB
    db, connection = create_db("lyrics.db")
    db.executemany('INSERT INTO songs VALUES (?,?,?)', results)
    connection.commit()
    connection.close()

