import database_helpers
import pandas as pd
import scrape_helpers

database_helpers.drop_database("database.db")
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
connection = database_helpers.create_database_connection("database.db")
database_helpers.insert_data(connection, data)
database_helpers.close_connection(connection)
