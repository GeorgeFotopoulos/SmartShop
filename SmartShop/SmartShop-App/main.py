import queue
import random
import threading
import time

import database_helpers
import natsort
import pandas as pd
import scrape_helpers

exceptions = []
database = "database.db"
products = queue.Queue()
start_time = time.time()
sleep_time = random.randint(2, 3)
landing_page = "https://www.sklavenitis.gr/"
categories_page = "https://www.sklavenitis.gr/katigories/"
data = pd.DataFrame(
    columns=["code", "store", "link", "product_name", "flat_price", "price_per_unit", "metric_unit"])

categories = scrape_helpers.scrape_categories(landing_page, categories_page)
""" scrape_helpers.scrape_products(landing_page, categories[0], products) """
threads = []
for category in categories:
    thread = threading.Thread(target=scrape_helpers.scrape_products,
                              args=(landing_page, category, products))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

categories_df = scrape_helpers.scrape_categories_ab(
    "https://api.ab.gr/?operationName=LeftHandNavigationBar&variables={%22lang%22:%22gr%22}&extensions={%22persistedQuery%22:{%22version%22:1,%22sha256Hash%22:%2229a05b50daa7ab7686d28bf2340457e2a31e1a9e4d79db611fcee435536ee01c%22}}",
)

""" category = categories_df.iloc[0]["category"]
pages = categories_df.iloc[0]["pages"]
for page in range(0, pages - 1):
    scrape_helpers.scrape_products_ab(
        "https://www.ab.gr",
        f"https://api.ab.gr/?operationName=GetCategoryProductSearch&variables={{%22category%22:%22{category}%22,%22pageNumber%22:{page}}}&extensions={{%22persistedQuery%22:{{%22version%22:1,%22sha256Hash%22:%227666accda68452ba9b05424ad98dec3cd402eacd9b896718a0a932975a0f405a%22}}}}",
        products,
        exceptions,
    )
    time.sleep(sleep_time) """

for index, row in categories_df.iterrows():
    category = row["category"]
    pages = row["pages"]
    for page in range(0, pages - 1):
        scrape_helpers.scrape_products_ab(
            "https://www.ab.gr",
            f"https://api.ab.gr/?operationName=GetCategoryProductSearch&variables={{%22category%22:%22{category}%22,%22pageNumber%22:{page}}}&extensions={{%22persistedQuery%22:{{%22version%22:1,%22sha256Hash%22:%227666accda68452ba9b05424ad98dec3cd402eacd9b896718a0a932975a0f405a%22}}}}",
            products,
            exceptions,
        )
        time.sleep(sleep_time)

scrape_helpers.scrape_product_exceptions_ab_recursive(exceptions, products)
while not products.empty():
    data = pd.concat(
        [data, pd.DataFrame(products.get(), index=[0])], ignore_index=True)
data = data.sort_values("price_per_unit", ascending=True)

database_helpers.drop_database(database)
connection = database_helpers.create_database_connection(database)
database_helpers.insert_data(connection, data)
database_helpers.close_connection(connection)

print(f"Total runtime: {time.time() - start_time} seconds")
