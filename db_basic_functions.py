import psycopg2
import yaml
import os
import pdb
from sshtunnel import SSHTunnelForwarder


def execute_sql(sql, args={}):
    config = {}
    yml_path = os.path.join(os.path.dirname(__file__), 'db.yml')
    with open(yml_path, 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    try:
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=config['user'],
                                ssh_password=config['password'],
                                remote_bind_address=('127.0.0.1', 5432)) as server:
            server.start()
            print("SSH tunnel established")
            conn = psycopg2.connect(dbname=config['database'],
                                    user=config['user'],
                                    password=config['password'],
                                    host=config['host'],
                                    port=server.local_bind_port)
            cur = conn.cursor()
            cur.execute(sql, args)
            conn.commit()
            list_of_tuples = cur.fetchall()
            conn.close()
            return list_of_tuples

    except Exception as e:
        print("Connection failed\n")
        print(e)


def execute_sql_fetch_one(sql, args={}):
    # Use this function when you're only expecting to get 1 value back from a select query so that you can easily use
    # result[0] to grab the value you want instead of having to do all of this nonsense just to collect an id in int
    # form: collection_id = int(str(collection_id[0])[1:-2]) where collection_id is the result of a SELECT query
    config = {}
    yml_path = os.path.join(os.path.dirname(__file__), 'db.yml')
    with open(yml_path, 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    try:
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=config['user'],
                                ssh_password=config['password'],
                                remote_bind_address=('127.0.0.1', 5432)) as server:
            server.start()
            print("SSH tunnel established")
            conn = psycopg2.connect(dbname=config['database'],
                                    user=config['user'],
                                    password=config['password'],
                                    host=config['host'],
                                    port=server.local_bind_port)
            cur = conn.cursor()
            cur.execute(sql, args)
            conn.commit()
            list_of_tuples = cur.fetchone()
            conn.close()
            return list_of_tuples

    except Exception as e:
        print("Connection failed\n")
        print(e)


def main():
    print(execute_sql("SELECT COUNT(*) FROM authors"))
    rate_book(7)




def rate_book(user_id):

    print(execute_sql("SELECT title FROM book"))
    book_to_rate = "%%" + input("Enter name of book you'd like to rate:")
    rating_to_give = input("Enter a rating of 1-5:")

    book_id_to_rate = execute_sql_fetch_one("SELECT bookid FROM book WHERE title LIKE '{}'".format(book_to_rate))

    sql_statement = "INSERT INTO rated (bookid, userid, rating) VALUES ('{}', '{}', '{}')".format(book_id_to_rate[0], user_id, rating_to_give)
    execute_sql(sql_statement)

    print(execute_sql("""SELECT book.bookid, book.title, rated.rating FROM rated INNER JOIN book 
                                            ON rated.bookid = book.bookid 
                                            WHERE rated.userid='{}'""".format(user_id)))


def add_book_to_collection(user_id):
    # Users can add and delete books from their collection Requirement

    print(execute_sql("""SELECT collection.collectionid, collection.name FROM collection INNER JOIN createcollection 
                                        ON collection.collectionid = createcollection.collectionid 
                                        WHERE userid='{}'""".format(user_id)))

    # Prompting the user to get name of the collection, need %% to make LIKE
    # clause work
    name_of_collection = "%%" + input("Which collection would you like to add a book to?")

    # This slightly complex query will get us the exact unique collectionId we want in order to find the exact
    # collection that needs a book added to it
    collection_id = execute_sql_fetch_one("""SELECT collection.collectionid FROM collection INNER JOIN createcollection 
                                        ON collection.collectionid = createcollection.collectionid 
                                        WHERE name LIKE '{}' AND userid='{}'""".format(name_of_collection,
                                                                                       user_id))

    print("Here is your collection of books:")
    print(execute_sql("""SELECT book.bookid, book.title, book.length, book.audience, book.releasedate FROM book INNER JOIN contains 
                                            ON book.bookid = contains.bookid 
                                            WHERE collectionid='{}'""".format(collection_id[0])))

    # Prompting the user to get necessary credentials for adding a book, need %% to make LIKE
    name_of_book = input("Enter title of book you would like to add:")
    length = input("Enter title length:")

    new_book_id = execute_sql_fetch_one("SELECT COUNT(bookid) FROM book")

    sql_statement = "INSERT INTO book (bookid, title, length) VALUES ('{}', '{}', '{}')".format(new_book_id[0] + 1, name_of_book, length)
    execute_sql(sql_statement)

    sql_statement = "INSERT INTO contains (bookid, collectionid) VALUES ('{}', '{}')".format(new_book_id[0] + 1,
                                                                                                collection_id[0])
    execute_sql(sql_statement)

    # Showing output of book table after adding
    print('book table within your collection after adding:')
    print(execute_sql("""SELECT book.bookid, book.title, book.length, book.audience, book.releasedate FROM book INNER JOIN contains 
                                                ON book.bookid = contains.bookid 
                                                WHERE collectionid='{}'""".format(collection_id[0])))


def delete_book_from_collection(user_id):
    # Users can add and delete books from their collection Requirement

    print(execute_sql("""SELECT collection.collectionid, collection.name FROM collection INNER JOIN createcollection 
                                    ON collection.collectionid = createcollection.collectionid 
                                    WHERE userid='{}'""".format(user_id)))

    # Prompting the user to get name of the collection, need %% to make LIKE
    # clause work
    name_of_collection = "%%" + input("Which collection would you like to delete a book from?")

    # This slightly complex query will get us the exact unique collectionId we want in order to find the exact
    # collection that needs a book deleted from it
    collection_id = execute_sql_fetch_one("""SELECT collection.collectionid FROM collection INNER JOIN createcollection 
                                    ON collection.collectionid = createcollection.collectionid 
                                    WHERE name LIKE '{}' AND userid='{}'""".format(name_of_collection,
                                                                                   user_id))

    print(execute_sql("""SELECT book.bookid, book.title, book.length, book.audience, book.releasedate FROM book INNER JOIN contains 
                                        ON book.bookid = contains.bookid 
                                        WHERE collectionid='{}'""".format(collection_id[0])))

    # Prompting the user to get name of the book, need %% to make LIKE
    # clause work
    name_of_book = "%%" + input("Which book would you like to delete?")

    # This slightly complex query will get us the exact unique bookId we want in order to find the exact
    # book that needs deleted
    book_id = execute_sql_fetch_one("""SELECT book.bookid FROM book INNER JOIN contains 
                                        ON book.bookid = contains.bookid 
                                        WHERE title LIKE '{}' AND collectionid='{}'""".format(name_of_book, collection_id[0]))

    sql_statement = "DELETE FROM book WHERE bookid={}".format(book_id[0])
    execute_sql(sql_statement)

    # Showing output of book table after deletion
    print('book table within your collection after deletion:')
    print(execute_sql("""SELECT book.bookid, book.title FROM book INNER JOIN contains 
                                            ON book.bookid = contains.bookid 
                                            WHERE collectionid='{}'""".format(collection_id[0])))


def change_name_of_collection(user_id):
    # Users can modify the name of a collection. They can also delete an entire collection Requirement

    # Displaying a table of collections for the user
    print(execute_sql("""SELECT collection.collectionid, collection.name FROM collection INNER JOIN createcollection 
                                ON collection.collectionid = createcollection.collectionid 
                                WHERE userid='{}'""".format(user_id)))

    # Prompting the user to get name of collection they want to change and what they want to change it to
    # %% must be appended to the beginning of name_of_collection_to_change for LIKE clause to work
    name_of_collection_to_change = "%%" + input('Enter name of collection to be re-named:')
    name_of_new_collection = input('Enter new name of collection:')

    # This slightly complex query will get us the exact unique collectionId we want in order to find the exact
    # collection that needs it's name changed
    collection_id = execute_sql_fetch_one("""SELECT collection.collectionid FROM collection INNER JOIN createcollection 
                                ON collection.collectionid = createcollection.collectionid 
                                WHERE name LIKE '{}' AND userid='{}'""".format(name_of_collection_to_change, user_id))

    # Finally updating/changing the name of the old collection to the new one
    sql_statement = "UPDATE collection SET name='{}' WHERE collectionid='{}'".format(name_of_new_collection, collection_id[0])
    execute_sql(sql_statement)

    # Showing output of collection table after name change
    print('collection table after update:')
    print(execute_sql("""SELECT collection.collectionid, collection.name FROM collection INNER JOIN createcollection 
                                    ON collection.collectionid = createcollection.collectionid 
                                    WHERE userid='{}'""".format(user_id)))


def delete_collection(user_id):
    # Users can modify the name of a collection. They can also delete an entire collection Requirement

    # Displaying a table of collections for the user
    print(execute_sql("""SELECT collection.collectionid, collection.name FROM collection INNER JOIN createcollection 
                                    ON collection.collectionid = createcollection.collectionid 
                                    WHERE userid='{}'""".format(user_id)))

    # Prompting the user to get name of collection they want to delete
    name_of_collection_to_delete = input('Enter name of collection to be deleted:')

    # appending % to the beginning of the string to make LIKE clause work
    name_of_collection_to_delete = "%%" + name_of_collection_to_delete

    # This slightly complex query will get us the exact unique collectionId we want in order to find the exact
    # collection that needs to be deleted
    collection_id = execute_sql_fetch_one("""SELECT collection.collectionid FROM collection INNER JOIN createcollection 
                                ON collection.collectionid = createcollection.collectionid 
                                WHERE name LIKE '{}' AND userid='{}'""".format(name_of_collection_to_delete, user_id))

    # This is a lot packed into one line, but bear with me.  collection_id is being returned to us from the sql query as
    # a tuple containing a string of (n,).  collection_id[0] is grabbing the 0 indexed element, it is then type casted
    # as a string by doing (str(collection_id[0]), we have [1: -2] at the end to cut off the ( from the beginning and
    # cut off ,) from the end of the string so we are left with just the number n. It is then once again type casted
    # but this time into an int by wrapping the whole thing with int.
    # collection_id = int(str(collection_id[0])[1:-2])
    # print(collection_id_what)
    # pdb.set_trace()
    # Finally deleting the desired collection
    sql_statement = "DELETE FROM collection WHERE collectionid={}".format(collection_id[0])
    execute_sql(sql_statement)

    # Showing output of collection table after deletion
    print('collection table after deletion:')
    print(execute_sql("""SELECT collection.collectionid, collection.name FROM collection INNER JOIN createcollection 
                                        ON collection.collectionid = createcollection.collectionid 
                                        WHERE userid='{}'""".format(user_id)))


main()
