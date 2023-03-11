from datetime import date

import firebase_admin
import pandas as pd
from firebase_admin import credentials, firestore


def open_database_connection():
    """
    Opens a connection to the Firestore database.

    Returns:
        firestore.client.Client: A reference to the Firestore client.
    """
    # Load the service account credentials
    cred = credentials.Certificate(
        "C:/Users/Admin/Downloads/smartshop-36cac-firebase-adminsdk-6do71-f5a277a5b3.json")

    # Initialize the Firebase app with the service account credentials
    firebase_admin.initialize_app(cred)

    # Return a reference to the Firestore client
    return firestore.client()


def close_database_connection(database):
    """
    Closes the connection to the Firestore database.

    Args:
        database (firestore.client.Client): A reference to the Firestore client.
    """
    database.close()


def get_all_products(database: firestore.client) -> pd.DataFrame:
    """Get all data from the 'products' collection.

    Args:
        database (firestore.client): A reference to the Firestore client.

    Returns:
        pd.DataFrame: A DataFrame containing all data from the 'products' collection.
    """
    products_ref = database.collection('products')
    docs = products_ref.get()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data)


def create_correlations(database: firestore.client, data: dict):
    """Create a collection in the database and write data to it.

    Args:
        database (firestore.client): A reference to the Firestore client.
        data (dict): A dictionary of key-value pairs to write to the collection.
    """
    print("Creating product correlations...")
    batch = database.batch()

    # Delete all documents in the 'correlations' collection
    docs = database.collection("correlations").get()
    for doc in docs:
        batch.delete(doc.reference)

    # Create new documents for each key-value pair in the dictionary
    for key, value in data.items():
        doc_ref = database.collection("correlations").document(key)
        batch.set(doc_ref, {'value': value})

    # Commit the batch write
    batch.commit()
    print("Finished creating product correlations.")


def create_products(database: firestore.client, data: pd.DataFrame):
    """Create a collection in the database and write data to it.
    Then insert a copy of data with the additional scan date column to products_history collection
    if the product code is the same but the price_per_unit or the final_price has changed.

    Args:
        database (firestore.client): A reference to the Firestore client.
        data (pd.DataFrame): The data that will be saved in the collection.
    """
    print("Creating products...")
    products_ref = database.collection("products")
    history_ref = database.collection("products_history")
    batch = database.batch()

    # Delete all documents in the 'products' collection
    for doc in products_ref.stream():
        batch.delete(doc.reference)

    # Create new data in 'products' collection
    for index, row in data.iterrows():
        doc_ref = products_ref.document(row['code'])
        batch.set(doc_ref, {
            'store': row['store'],
            'link': row['link'],
            'product_name': row['product_name'],
            'starting_price': row['starting_price'],
            'final_price': row['final_price'],
            'price_per_unit': row['price_per_unit'],
            'metric_unit': row['metric_unit'],
            'discounted': row['discounted']
        })

    # Commit the batch write to 'products' collection
    batch.commit()

    # Check if the new data has any changes to starting_price compared to the existing data
    existing_data = history_ref.where(
        'scan_date', '==', date.today().strftime("%Y-%m-%d")).get()
    existing_data_dict = {doc.to_dict()['code']: doc.to_dict()[
        'starting_price'] for doc in existing_data}
    batch = database.batch()

    # Create new data in 'products_history' collection
    for index, row in data.iterrows():
        if row['code'] in existing_data_dict and row['starting_price'] == existing_data_dict[row['code']]:
            continue
        doc_ref = history_ref.document()
        batch.set(doc_ref, {
            'code': row['code'],
            'store': row['store'],
            'link': row['link'],
            'product_name': row['product_name'],
            'starting_price': row['starting_price'],
            'final_price': row['final_price'],
            'price_per_unit': row['price_per_unit'],
            'metric_unit': row['metric_unit'],
            'discounted': row['discounted'],
            'scan_date': date.today().strftime("%Y-%m-%d")
        })

    # Commit the batch write to 'products_history' collection
    batch.commit()
    print("Finished creating products.")
