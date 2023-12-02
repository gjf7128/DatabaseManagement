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
            cur.execute(sql)
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

def register(username, password, fname, lname, email):
    sql_query = "SELECT userid FROM USERS ORDER BY accountcreated DESC LIMIT 1;"
    newest = execute_sql(sql_query)[0][0] + 1
    value_template = "(" + str(newest) + ",'" + username + "','" + password + "','" + fname + "','" + lname + "','" + email + "',CURRENT_DATE,CURRENT_DATE);"
    value_string = str.format(value_template, {username, password, fname, lname, email})
    sql_query = "INSERT INTO users(userid, username, password, firstname, lastname, email, accountcreated, lastaccessed) VALUES" + value_string
    execute_sql(sql_query)

def login(username, password):
    sql_query = "SELECT userID,password FROM USERS WHERE username = '" + username + "';"
    try:
        user = execute_sql(sql_query)[0]
        if(password == user[1]):
            return user[0]
    except:
        return -1

def read_book(book_id, person_id, start_page, end_page):
    # User can read book by selecting the page to start and the page to end
    # There is no read functionality for the user, user should only be able to mark a book as read
    # Function ADDS a new row to "read" table where the book being read, user reading, ammount of pages read, and the date where this rading took place is recorded
    # Function still needs work
    pagesRead = end_page - start_page
    sqlStatement = 'INSERT INTO read(bookid, userid, pages) VALUES ({}, {}, {})'.format(book_id, person_id, pagesRead)
    execute_sql(sqlStatement)

def search_books_by_title(title):
    sql_query = "SELECT * FROM book WHERE title LIKE '%" + title + "%';"
    return execute_sql(sql_query)

def search_books_by_release_date_before(date):
    sql_query = "SELECT * FROM book WHERE releasedate < CAST('" + date + "' as date);"
    return execute_sql(sql_query)

def search_books_by_release_date_after(date):
    sql_query = "SELECT * FROM book WHERE releasedate > CAST('" + date + "' as date);"
    return execute_sql(sql_query)

def search_books_by_author(author):
    sql_query = """SELECT * FROM person LEFT JOIN authors ON person.personID = authors.personID 
                    LEFT JOIN book ON authors.bookID = book.bookID WHERE person.firstname = '""" + author + "';"
    return execute_sql(sql_query)

def search_books_by_editor(editor):
    sql_query = """SELECT * FROM person LEFT JOIN edits ON person.personID = edits.personID 
                    LEFT JOIN book ON edits.bookID = book.bookID WHERE person.firstname = '""" + editor + "';"
    return execute_sql(sql_query)

def search_books_by_publisher(publisher):
    sql_query = """SELECT * FROM person LEFT JOIN publishes ON person.personID = publishes.personID 
                    LEFT JOIN book ON publishes.bookID = book.bookID WHERE person.firstname = '""" + publisher + "';"
    return execute_sql(sql_query)

def search_books_by_genre(genre):
    sql_query = """SELECT * FROM genre LEFT JOIN bookgenre ON genre.genreID = bookgenre.genreID
                    LEFT JOIN book ON book.bookID = bookgenre.bookID where genre.name = '""" + genre + "';"
    return execute_sql(sql_query)

def create_collection(userid, collection_name):
    sql_query = """INSERT INTO collection(name) VALUES('""" + collection_name + "');"
    execute_sql(sql_query)
    sql_query = """SELECT collectionid FROM collection where collection_name = '""" + collection_name + "';"
    collectionid = execute_sql(sql_query)
    sql_query = """INSERT INTO createcollection(userid, collection id) VALUES (""" + userid + ',' + collectionid + ");"

def get_collections(userid):
    sql_query = """SELECT collection.name, COUNT(contains.BookID), SUM(book.Length) FROM 
                    User JOIN createCollection ON UserID = createCollection.UserID 
                    JOIN collection ON createCollection.CollectionID = collection.CollectionID
                    LEFT JOIN contains ON collection.CollectionID = contains.CollectionID
                    LEFT JOIN book ON contains.BookID = book.BookID
                    WHERE UserID = """ + str(userid) + """ GROUP BY collection.CollectionID, collection.Name ORDER BY collection.CollectionID;"""
    return execute_sql(sql_query)

def follow_user(userID, otherEmail):
    sql_query = "SELECT userid from users where email = '" + otherEmail + "';"
    otherUser = execute_sql(sql_query)[0][0]
    sql_query = "INSERT INTO followers(followerid, followeeid) VALUES(" + str(userID) + "," + str(otherUser) + ");"
    execute_sql(sql_query)

def unfollow_user(userID, otherEmail):
    sql_query = "SELECT userid from users where email = '" + otherEmail + "';"
    otherUser = execute_sql(sql_query)[0][0]
    sql_query = "DELETE FROM followers WHERE followerID = " + str(userID) + " AND followeeID = " + str(otherUser) + ";"
    execute_sql(sql_query)

def main():
    print(register("user98", "password98", "Jensen", "DeRosier", "jld3877@rit.edu"))

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

def most_pop_90_days():
    sql_query = """SELECT book.Title FROM read JOIN book ON read.bookID = book.bookID
                        WHERE read.date >= CURRENT_DATE - 90 
                        GROUP BY book.bookID ORDER BY COUNT(book.bookID) DESC
                        LIMIT 20;"""
    return(execute_sql(sql_query))

def most_pop_among_followers(user_id):
    sql_query = """SELECT book.title 
                    FROM followers JOIN read ON followers.followerID = read.userID
                    JOIN book ON read.bookID = book.bookID
                    WHERE followers.followeeID = """ + (str)(user_id) + """
                    GROUP BY book.bookID ORDER BY COUNT(book.bookID)
                    LIMIT 20;
                    """
    return(execute_sql(sql_query))

def top_5_calendar_month():
    sql_query = """SELECT title FROM book JOIN read ON book.bookID = read.bookID
                    WHERE EXTRACT(MONTH FROM releasedate) = EXTRACT(MONTH FROM CURRENT_DATE) AND EXTRACT(YEAR FROM releasedate) = EXTRACT(YEAR FROM CURRENT_DATE)
                    GROUP BY book.bookID ORDER BY COUNT(book.bookID)"""
    return(execute_sql(sql_query))

def recommend_genre_history(user_id):
    sql_query = """WITH UserGenres AS (
                    SELECT genre.genreID, AVG(rated.rating) as AvgRating
                    FROM rated JOIN bookgenre ON rated.bookID = bookgenre.BookID
                    JOIN genre ON bookgenre.genreID = genre.genreID
                    WHERE rated.userID = """ + str(user_id) + """
                    GROUP BY genre.genreID)

                    SELECT book.title
                    FROM usergenres JOIN bookgenre on usergenres.genreID = bookgenre.genreID
                    JOIN book ON book.bookID = bookgenre.bookID
                    ORDER BY AvgRating DESC LIMIT 10;"""
    return(execute_sql(sql_query))

def recommend_author_history(user_id):
    sql_query = """WITH UserFavAuthors AS (
                    SELECT personID, AVG(rated.rating) as AvgRating
                    FROM rated JOIN authors ON rated.bookID = authors.bookID
                    WHERE rated.userID = """ + str(user_id) + """
                    GROUP BY authors.personID)

                    SELECT book.Title
                    FROM UserFavAuthors JOIN authors on UserFavAuthors.personID = authors.personID
                    JOIN book ON book.bookID = authors.bookID
                    ORDER BY AvgRating DESC LIMIT 10;"""
    return(execute_sql(sql_query))


def main():
    print(most_pop_among_followers(1))

def get_num_collections_for_user(user_id):
    # The number of collections the user has requirement
    print('\n now within get_num_collections_for_user')
    collections_table = execute_sql_fetch_one("""SELECT COUNT(*) FROM (SELECT collection.collectionid, collection.name inneralias FROM collection INNER JOIN createcollection 
                                    ON collection.collectionid = createcollection.collectionid 
                                    WHERE userid='{}') outeralias""".format(user_id))
    print('\n')
    print(collections_table[0])
    print('\n')

def get_num_users_this_user_follows(user_id):
    # The number of users this user follows
    print('\n getting the number of users this user follows: \n')

    num_followers = execute_sql_fetch_one("""SELECT COUNT(*) FROM followers WHERE followerid='{}'""".format(user_id))

    print(num_followers[0])
    print('\n')

def get_num_followers_this_user_has(user_id):
    # The number of followers this user has
    print('\n getting the number of followers this user has: \n')

    num_followers = execute_sql_fetch_one("""SELECT COUNT(*) FROM followers WHERE followeeid='{}'""".format(user_id))

    print(num_followers[0])
    print('\n')

def get_users_top_ten_books_times_read(user_id):
    # Get top 10 books by highest rating, most read, or combination
    print('\n getting users top ten books by times read \n')

    table = execute_sql("""SELECT book.title FROM read JOIN book ON read.bookid = book.bookid WHERE read.userid = '{}' 
    GROUP BY book.bookid ORDER BY COUNT(book.bookid) DESC LIMIT 10""".format(user_id))

    print(table)
    print('\n')

def get_users_top_ten_books_combo(user_id):
    # Get top 10 books by highest rating, most read, or combination
    print('\n getting users top ten books by times read and rating \n')

    table = execute_sql("""SELECT book.title, rated.rating FROM read JOIN book ON read.bookid = book.bookid JOIN rated 
    ON book.bookid = rated.bookid WHERE read.userid = '{}' GROUP BY book.bookid, rated.rating ORDER BY COUNT(book.bookid) 
    DESC , rated.rating DESC LIMIT 10""".format(user_id))


    print(table)
    print('\n')

def get_users_top_ten_books_rating(user_id):
    # Get top 10 books by highest rating, most read, or combination
    print('\n getting users top ten books by rating \n')

    table = execute_sql("""SELECT book.title, rated.rating FROM rated JOIN book ON rated.bookid = book.bookid WHERE 
    rated.userid = '{}' ORDER BY rated.rating DESC LIMIT 10""".format(user_id))

    print(table)
    print('\n')

if __name__ == "__main__":
    main()