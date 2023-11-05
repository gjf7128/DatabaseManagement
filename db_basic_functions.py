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
    delete_collection(69)



def addBookToCollection(collectionid, bookid):
    # Users can add and delete books from their collection Requirement
    # This function is just for ADDING
    # This function still needs work
    sqlStatement = 'INSERT INTO contains(collectionid, bookid) VALUES ({}, {})'.format(collectionid, bookid)
    return execute_sql(sqlStatement)


def deleteBookFromCollection(collectionid, bookid):
    # Users can add and delete books from their collection Requirement
    # This function is just for DELETING
    # This function still needs work
    sqlStatement = 'DELETE FROM contains WHERE collectionid={} AND bookid={}'.format(collectionid, bookid)
    return execute_sql(sqlStatement)


def insert_into_collection_for_testing(collectionid, bookid):
    # Users can add and delete books from their collection Requirement
    # This function is just for ADDING
    # This function still needs work
    sqlStatement = 'INSERT INTO contains(collectionid, bookid) VALUES ({}, {})'.format(collectionid, bookid)
    return execute_sql(sqlStatement)


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

    # Showing output of collection table after name change
    print('collection table after deletion:')
    print(execute_sql("""SELECT collection.collectionid, collection.name FROM collection INNER JOIN createcollection 
                                        ON collection.collectionid = createcollection.collectionid 
                                        WHERE userid='{}'""".format(user_id)))


main()
