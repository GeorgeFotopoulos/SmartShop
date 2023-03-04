import queue
import random
import threading
import time

import database_helpers
import pandas as pd
import scrape_helpers

threads = []
exceptions = []
database = "database.db"
products = queue.Queue()
start_time = time.time()
data = pd.DataFrame(columns=["code", "store", "link", "product_name",
                    "starting_price", "final_price", "price_per_unit", "metric_unit", "discounted"])

categories = scrape_helpers.scrape_categories(
    "https://www.sklavenitis.gr/", "https://www.sklavenitis.gr/katigories/")
total_progress = len(categories)
completed_progress = 0

for category in categories:
    thread = threading.Thread(target=scrape_helpers.scrape_products, args=(
        "https://www.sklavenitis.gr/", category, products))
    threads.append(thread)
    thread.start()

while threads:
    thread_count = len(threads)
    for i in range(thread_count):
        if not threads[i].is_alive():
            completed_progress += 1
            threads[i].join()
            threads.pop(i)
            break
    if thread_count == len(threads):
        time.sleep(1)
    progress = completed_progress / total_progress
    progress_bar_length = 50
    filled_length = int(progress * progress_bar_length)
    bar = "#" * filled_length + "-" * (progress_bar_length - filled_length)
    print(f"\rScraping Σκλαβενίτης... [{bar}] {int(progress * 100)}%", end="")

duration_seconds = time.time() - start_time
minutes, seconds = divmod(duration_seconds, 60)
print(
    f"Scraping Σκλαβενίτης complete, runtime: {int(minutes)} minutes, {int(seconds)} seconds")

start_time = time.time()
categories_df = scrape_helpers.scrape_categories_ab(
    "https://api.ab.gr/?operationName=LeftHandNavigationBar&variables={%22lang%22:%22gr%22}&extensions={%22persistedQuery%22:{%22version%22:1,%22sha256Hash%22:%2229a05b50daa7ab7686d28bf2340457e2a31e1a9e4d79db611fcee435536ee01c%22}}",
)

total_pages = categories_df["pages"].sum()
completed_pages = 0
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
        completed_pages += 1
        progress = completed_pages / total_pages
        progress_bar_length = 50
        filled_length = int(progress * progress_bar_length)
        bar = "#" * filled_length + "-" * (progress_bar_length - filled_length)
        print(
            f"\rScraping ΑΒ Βασιλόπουλος... [{bar}] {int(progress * 100)}%", end="")
        time.sleep(random.randint(2, 3))

scrape_helpers.scrape_product_exceptions_ab_recursive(exceptions, products)
while not products.empty():
    data = pd.concat(
        [data, pd.DataFrame(products.get(), index=[0])], ignore_index=True)

data = data.drop_duplicates()

database_helpers.drop_database(database)
connection = database_helpers.create_database_connection(database)
database_helpers.insert_data(connection, data)
database_helpers.close_connection(connection)

duration_seconds = time.time() - start_time
minutes, seconds = divmod(duration_seconds, 60)
print(
    f"Scraping ΑΒ Βασιλόπουλος complete, runtime: {int(minutes)} minutes, {int(seconds)} seconds")
