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

def main():
    print(execute_sql("SELECT COUNT(*) FROM authors"))

def addBookToCollection(collectionid, bookid):
    #Users can add and delete books from their collection
    #columns of collection are: collectionid, name, userid
    #insert into contains table (bookid, columnid) VALUES (book.id, collection.id)
    sqlStatement = 'INSERT INTO contains(collectionid, bookid) VALUES ()'
    return sqlStatement

main()