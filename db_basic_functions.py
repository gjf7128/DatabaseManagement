import psycopg2
import yaml
import os
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
    unfollow_user(5, "johndoe@example.com")

if __name__ == "__main__":
    main()