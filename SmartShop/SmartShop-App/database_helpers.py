import os
import sqlite3

import pandas


def drop_database(database):
    """
    Drops and recreates the database.

    Parameters:
        database (Literal): The database name.
    """

    if os.path.exists(database):
        os.remove(database)


def create_database_connection(database):
    """
    Creates connection to the database.

    Parameters:
        database (Literal): The database name.

    Returns:
        TODO
    """

    return sqlite3.connect(database)


def close_connection(connection: sqlite3.Connection):
    """
    Closes the connection to the database.

    Parameters:
        connection: The connection that was opened earlier.
    """

    connection.close()


def insert_data(connection: sqlite3.Connection, data: pandas.DataFrame):
    """
    Inserts all data to the products table.

    Parameters:
        database (Literal): The database name.
        data (DataFrame): The data that will be saved in the database.
    """

    connection.execute(
        "CREATE TABLE products (code TEXT PRIMARY KEY, store TEXT, link TEXT, product_name TEXT, flat_price REAL, price_per_unit REAL, metric_unit TEXT)")
    connection.commit()
    data.to_sql("products", connection, if_exists="append", index=False)


def delete_data(connection: sqlite3.Connection):
    """
    Deletes all data from the products table.

    Parameters:
        database (Literal): The database name.
    """

    connection.execute("DELETE FROM products")
    connection.commit()
