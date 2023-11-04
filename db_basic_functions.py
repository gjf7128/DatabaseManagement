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


def change_name_of_collection(user_id):
    # Users can modify the name of a collection. They can also delete an entire collection Requirement

    # Prompting the user to get name of collection they want to change and what they want to change it to
    name_of_collection_to_change = input('Enter name of collection to be re-named')
    name_of_new_collection = input('Enter new name of collection')

    # appending % to the beginning of the string to make LIKE clause work
    name_of_collection_to_change = '%' + name_of_collection_to_change

    # This slightly complex query will get us the exact unique collectionId we want in order to find the exact
    # collection that needs it's name changed
    collection_id = execute_sql('SELECT collection.collectionid FROM collection INNER JOIN createcollection '
                                'ON collection.collectionid = createcollection.collectionid '
                                'WHERE name LIKE {} AND userid={}').format(name_of_collection_to_change, user_id)

    # Finally updating/changing the name of the old collection to the new one
    sql_statement = 'UPDATE collection SET name={} WHERE collectionid={}'.format(name_of_new_collection, collection_id)
    return sql_statement


def delete_collection(user_id):
    # Users can modify the name of a collection. They can also delete an entire collection Requirement

    # Prompting the user to get name of collection they want to delete
    name_of_collection_to_delete = input('Enter name of collection to be deleted')

    # appending % to the beginning of the string to make LIKE clause work
    name_of_collection_to_delete = '%' + name_of_collection_to_delete

    # This slightly complex query will get us the exact unique collectionId we want in order to find the exact
    # collection that needs to be deleted
    collection_id = execute_sql('SELECT collection.collectionid FROM collection INNER JOIN createcollection '
                                'ON collection.collectionid = createcollection.collectionid '
                                'WHERE name LIKE {} AND userid={}').format(name_of_collection_to_delete, user_id)

    # Finally deleting the desired collection
    sql_statement = 'DELETE FROM collection WHERE collectionid={}'.format(collection_id)
    return sql_statement


main()
