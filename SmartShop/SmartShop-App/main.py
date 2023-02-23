from database_helpers import *
from scrape_helpers import *

import pandas as pd
import threading
import time
import queue

categories = []
database = 'database.db'
products = queue.Queue()
start_time = time.time()
landing_page = 'https://www.sklavenitis.gr/'
categories_page = 'https://www.sklavenitis.gr/katigories/'
data = pd.DataFrame(columns=['link', 'product_name',
                    'flat_price', 'price_per_unit'])

scrape_categories(landing_page, categories_page, categories)
""" categories.append(
    'https://www.sklavenitis.gr/turokomika-futika-anapliromata/feta-leyka-tyria/') """

threads = []
for category in categories:
    thread = threading.Thread(target=scrape_products,
                              args=(landing_page, category, products))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

while not products.empty():
    new_row = pd.DataFrame([products.get()])
    data = pd.concat([data, new_row], ignore_index=True)
data = data.sort_values(by=['price_per_unit'])

drop_database(database)
connection = create_database_connection(database)
insert_data(connection, data)

fetch_data_from_database(connection)
close_connection(connection)

end_time = time.time()
total_time = end_time - start_time
print(f"Total runtime: {total_time} seconds")
