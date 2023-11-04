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
            cur.execute(sql, args)
            conn.commit()
            list_of_tuples = cur.fetchall()
            conn.close()
            return list_of_tuples
        
    except Exception as e:
        print("Connection failed\n")
        print(e)

def read_book(book_id, person_id, start_page, end_page, date):
    # User can read book by selecting the page to start and the page to end
    # There is no read functionality for the user, user should only be able to mark a book as read
    # Function ADDS a new row to "read" table where the book being read, user reading, ammount of pages read, and the date where this rading took place is recorded
    # Function still needs work
    pagesRead = end_page - start_page
    sqlStatement = 'INSERT INTO read(bookid, userid, pages, date) VALUES ({}, {}, {})'.format(book_id, person_id, pagesRead, date)

    

def main():
    print(execute_sql("SELECT COUNT(*) FROM authors"))

main()