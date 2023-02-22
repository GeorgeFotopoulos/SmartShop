import os
import sqlite3


def create_connection(database):
    """
    Creates connection to the database.

    Parameters:
    database (Literal): The database name.
    """

    connection = sqlite3.connect(database)
    return connection


def close_connection(connection: sqlite3.Connection):
    """
    Closes the connection to the database.

    Parameters:
    connection: The connection that was opened earlier.
    """

    connection.close()


def drop_create_database(database):
    """
    Drops and recreates the database.

    Parameters:
    database (Literal): The database name.
    """

    if os.path.exists(database):
        os.remove(database)


def insert_data(connection: sqlite3.Connection, data):
    """
    Inserts all data to the products table.

    Parameters:
    database (Literal): The database name.
    data (DataFrame): The data that will be saved in the database.
    """

    connection.execute(
        'CREATE TABLE products (id INTEGER PRIMARY KEY, link TEXT, product_name TEXT, flat_price REAL, price_per_unit REAL)')
    connection.commit()
    data.to_sql('products', connection, if_exists='append', index=False)


def delete_data(connection: sqlite3.Connection):
    """
    Deletes all data from the products table.

    Parameters:
    database (Literal): The database name.
    """

    connection.execute('DELETE FROM products')
    connection.commit()


def fetch_data_from_database(connection: sqlite3.Connection):
    """
    Fetches all data from products table.

    Parameters:
    database (Literal): The database name.
    """

    cursor = connection.execute("SELECT * FROM products")

    """ rows = cursor.fetchall()
    for row in rows:
        print(row) """

    cursor.close()
    connection.close()
