import os
import sqlite3

import pandas as pd


def drop_database(database):
    """Drops and recreates the database.

    Args:
        database (Literal): The database name.
    """
    if os.path.exists(database):
        os.remove(database)


def create_database_connection(database):
    """Creates a connection to the specified database.

    Args:
        database (str): The name of the database to connect to.

    Returns:
        sqlite3.Connection: A connection to the specified database.
    """
    return sqlite3.connect(database)


def close_database_connection(connection: sqlite3.Connection):
    """Closes the connection to the database.

    Args:
        connection: The connection that was opened earlier.
    """
    connection.close()


def create_products(connection: sqlite3.Connection, data: pd.DataFrame):
    """Create a 'products' table in the database and write data to it.

    Args:
        connection (sqlite3.Connection): A connection to the SQLite database.
        data (pd.DataFrame): The data that will be saved in the database.
    """
    connection.execute("DROP TABLE IF EXISTS products;")
    data.to_sql("products", connection, if_exists="replace", index=False, dtype={
        'code': 'TEXT',
        'store': 'TEXT',
        'link': 'TEXT',
        'product_name': 'TEXT',
        'starting_price': 'REAL',
        'final_price': 'REAL',
        'price_per_unit': 'REAL',
        'metric_unit': 'TEXT',
        'discounted': 'INTEGER'})
    connection.commit()


def get_all_products(connection: sqlite3.Connection) -> pd.DataFrame:
    """Get all data from the 'products' table.

    Args:
        connection (sqlite3.Connection): A connection to the SQLite database.

    Returns:
        pd.DataFrame: A DataFrame containing all data from the 'products' table.
    """
    query = "SELECT * FROM products;"
    return pd.read_sql_query(query, connection)


def create_correlations(connection: sqlite3.Connection, data: dict):
    """Create a 'correlations' table in the database and write data to it.

    Args:
        connection (sqlite3.Connection): A connection to the SQLite database.
        data (dict): A dictionary of key-value pairs to write to the 'correlations' table.
    """
    connection.execute("DROP TABLE IF EXISTS correlations;")
    df = pd.DataFrame.from_dict(data, orient='index', columns=['value'])
    df.index.name = 'key'
    df.to_sql("correlations", connection, index=True,
              dtype={'key': 'TEXT', 'value': 'TEXT'})
    connection.commit()
