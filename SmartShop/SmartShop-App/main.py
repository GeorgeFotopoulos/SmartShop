import correlation_helpers
import database_helpers
import pandas as pd
import scrape_helpers

data = pd.DataFrame(columns=["code", "store", "link", "product_name",
                    "starting_price", "final_price", "price_per_unit", "metric_unit", "discounted"])

# Scrape the data
products_sklavenitis = scrape_helpers.scrape_sklavenitis()
products_ab = scrape_helpers.scrape_ab()

while not products_sklavenitis.empty():
    data = pd.concat(
        [data, pd.DataFrame(products_sklavenitis.get(), index=[0])], ignore_index=True)

while not products_ab.empty():
    data = pd.concat(
        [data, pd.DataFrame(products_ab.get(), index=[0])], ignore_index=True)

data = data.drop_duplicates()

# Insert the data into the database
connection = database_helpers.create_database_connection("database.db")
database_helpers.create_products(connection, data)
database_helpers.create_correlations(
    connection, correlation_helpers.get_correlations(database_helpers.get_all_products(connection)))
database_helpers.close_database_connection(connection)
