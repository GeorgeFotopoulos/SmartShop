from datetime import date

import correlation_helpers
import database_helpers
import firebase_helpers
import pandas as pd
import scrape_helpers


def main_firebase():
    connection = database_helpers.create_database_connection("database.db")
    data = database_helpers.get_all_products(connection)
    correlations = correlation_helpers.get_correlations(data)
    database_helpers.close_database_connection(connection)

    database = firebase_helpers.open_database_connection()
    firebase_helpers.create_correlations(database, correlations)
    firebase_helpers.create_products(database, data)
    firebase_helpers.close_database_connection(database)


def main_sqlite():
    connection = database_helpers.create_database_connection("database.db")

# data = database_helpers.get_all_products(connection)
    data = pd.DataFrame(columns=["code", "store", "link", "product_name",
                                 "starting_price", "final_price", "price_per_unit", "metric_unit", "discounted"])

    products_sklavenitis = scrape_helpers.scrape_sklavenitis()
    products_ab = scrape_helpers.scrape_ab()

    while not products_sklavenitis.empty():
        data = pd.concat(
            [data, pd.DataFrame(products_sklavenitis.get(), index=[0])], ignore_index=True)

    while not products_ab.empty():
        data = pd.concat(
            [data, pd.DataFrame(products_ab.get(), index=[0])], ignore_index=True)

    data = data.drop_duplicates()
    database_helpers.create_products(
        connection, data, date.today().strftime("%Y-%m-%d"))

    print("Creating product correlations...")
    correlations = correlation_helpers.get_correlations(data)
    database_helpers.create_correlations(connection, correlations)
    database_helpers.close_database_connection(connection)
    print("All operations finished successfully.")


# main_firebase()
# main_sqlite()
