import queue
import threading
import time

import database_helpers
import natsort
import pandas
import scrape_helpers

database = 'database.db'
products = queue.Queue()
""" start_time = time.time() """
landing_page = 'https://www.sklavenitis.gr/'
categories_page = 'https://www.sklavenitis.gr/katigories/'
data = pandas.DataFrame(columns=['shop', 'link', 'product_name',
                                 'flat_price', 'price_per_unit'])

categories = scrape_helpers.scrape_categories(landing_page, categories_page)
""" categories.append(
	'https://www.sklavenitis.gr/turokomika-futika-anapliromata/feta-leyka-tyria/') """

""" threads = []
for category in categories:
    thread = threading.Thread(target=scrape_helpers.scrape_products,
                              args=(landing_page, category, products))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join() """

while not products.empty():
    new_row = pandas.DataFrame([products.get()])
    data = pandas.concat([data, new_row], ignore_index=True)
data = data.iloc[natsort.index_humansorted(data['price_per_unit'])]

database_helpers.drop_database(database)
connection = database_helpers.create_database_connection(database)
database_helpers.insert_data(connection, data)

database_helpers.fetch_data_from_database(connection)
database_helpers.close_connection(connection)


categories = scrape_helpers.scrape_categories_using_webdriver(
    'https://www.ab.gr/')

threads = []
for category in categories:
    thread = threading.Thread(target=scrape_helpers.scrape_products2,
                              args=(landing_page, category, products))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

while not products.empty():
    new_row = pandas.DataFrame([products.get()])
    data = pandas.concat([data, new_row], ignore_index=True)
data = data.iloc[natsort.index_humansorted(data['price_per_unit'])]

pass
""" end_time = time.time()
total_time = end_time - start_time
print(f"Total runtime: {total_time} seconds") """
