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
    #Users can add and delete books from their collection Requirement
    #This function is just for ADDING
    #This function still needs work
    sqlStatement = 'INSERT INTO contains(collectionid, bookid) VALUES ({}, {})'.format(collectionid, bookid)
    return execute_sql(sqlStatement)

def deleteBookFromCollection(collectionid, bookid):
    #Users can add and delete books from their collection Requirement
    #This function is just for DELETING
    #This function still needs work
    sqlStatement = 'DELETE FROM contains WHERE collectionid={} AND bookid={}'.format(collectionid, bookid)
    return execute_sql(sqlStatement)

def changeNameOfCollection(userId):
    #Users can modify the name of a collection. They can also delete an entire collection Requirement
    #Use this function like this: cur.execute(deleteBookFromCollection(collectionid, bookid))
    nameOfCollectionToDelete = input('Enter name of collection to be re-named')
    nameOfNewCollection = input('Enter new name of collection')

    #The following LOC depends on collecting userId at login
    #Actually... users have many collections and have many collectionid's... so this wont work.  might need a complex query
    #This would give a list of collectionid's when we really want a specific collectionid... might need JOIN collection and createcollection
    #then SELECT collectionid where collection.name = nameOfCollectiontoDelete AND userId = createcollection.userid?
    collectionId = execute_sql('SELECT collectionid FROM createcollection WHERE userid={}').format(userId)

    #Definitely going to need collectionid and name to
    sqlStatement = 'UPDATE collection SET name={} WHERE collectionid={}'.format()
    return sqlStatement

main()