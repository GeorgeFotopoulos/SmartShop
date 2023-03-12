import json
import math
import queue
import random
import re
import threading
import time
import urllib
from typing import List
from urllib.request import urlopen

import pandas
import requests
from bs4 import BeautifulSoup

threads = []
exceptions = []
products_sklavenitis = queue.Queue()
products_ab = queue.Queue()


def scrape_sklavenitis():
    start_time = time.time()
    categories = scrape_categories_sklavenitis(
        "https://www.sklavenitis.gr/", "https://www.sklavenitis.gr/katigories/")
    total_progress = len(categories)
    completed_progress = 0

    for category in categories:
        thread = threading.Thread(target=scrape_products_sklavenitis, args=(
            "https://www.sklavenitis.gr/", category))
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
        print(
            f"\rScraping Σκλαβενίτης... [{bar}] {int(progress * 100)}%", end="")

    duration_seconds = time.time() - start_time
    minutes, seconds = divmod(duration_seconds, 60)
    print(
        f"\nScraping Σκλαβενίτης complete, runtime: {int(minutes)} minutes, {int(seconds)} seconds")
    return products_sklavenitis


def scrape_categories_sklavenitis(landing_page, categories_page) -> List[str]:
    """
    Parses the categories within each store, in order to get the links to all categories.

    Parameters:
        landing_page (Literal): Indicates the landing page of a particular store.
        categories_page (Literal): Indicates the categories page within the website.

    Returns:
        TODO
    """

    categories = []
    ignore_list = ["vrefika", "thymiamatos", "katoikidia", "etoima-geymata"]
    response = requests.get(categories_page)
    soup = BeautifulSoup(response.text, "html.parser")
    ul_mainNav = soup.find("ul", {"class": "mainNav_ul"})
    lis = ul_mainNav.find_all("li")

    for li in lis:
        ul_mainNav_sub = li.find("ul", {"class": "mainNav_sub"})
        if ul_mainNav_sub:
            a_tags = ul_mainNav_sub.find_all("a")
            for a in a_tags:
                if not any(word in a["href"] for word in ignore_list):
                    categories.append(landing_page + a["href"])
    return categories


def scrape_products_sklavenitis(prefix, category):
    """
    Iterates all pages within a category, necessary due to pagination.
    Breaks when there are no more product links provided.

    Parameters:
        prefix (Literal): The category url that contains all objects that will be scraped for data.
        category (str): A particular category that will be parsed for all its products' data to be scraped.
    """

    i = 1
    has_products = True

    while has_products:
        response = requests.get(category + f"?pg={i}")
        soup = BeautifulSoup(response.content, "html.parser")
        products_list = soup.find_all(
            "div", class_=re.compile("^product prGa_"))

        if not products_list:
            has_products = False
            continue

        for product in products_list:
            scrape_data_sklavenitis(prefix, product)

        i += 1


def scrape_data_sklavenitis(prefix, product):
    """
    Scrapes product link, name, flat price and price per unit.

    Parameters:
        prefix (Literal): The prefix to add to the url for each particular product.
        product (BeautifulSoup): A particular product's soup variable, to extract the data from.
    """

    element = product.find(
        "div", class_="icon-fav icon-cartFav")["data-productsku"]
    if element:
        code = element

    element = product.find("a", class_="absLink")["href"]
    if element:
        link = prefix + element

    element = product.find("h4", class_="product__title")
    if element:
        product_name = element.text.replace("\n", "")

    starting_price = None
    element = product.find("div", class_="deleted__price")
    if element:
        starting_price = element.text.replace(",", ".")

    element = product.find("div", class_="price")
    if element:
        final_price = element.text.split()[0].replace(",", ".").strip()

    if not starting_price:
        starting_price = final_price

    element = product.find("div", class_="hightlight")
    if element:
        price_per_unit = element.text
    else:
        element = product.find("div", class_="priceKil")
        if element and element.text:
            price_per_unit = element.text
        else:
            price_per_unit = final_price

    if price_per_unit:
        try:
            parts = price_per_unit.replace("~", "").strip().split()
            price_per_unit = float(parts[0].replace(",", ".").strip())
            metric_unit = parts[1].strip()
        except (ValueError, IndexError):
            price_per_unit = None
            metric_unit = None
    else:
        price_per_unit = 0.00
        metric_unit = None

    new_row = {
        "code": code,
        "store": "Σκλαβενίτης",
        "link": link,
        "product_name": product_name,
        "starting_price": starting_price,
        "final_price": final_price,
        "price_per_unit": price_per_unit,
        "metric_unit": metric_unit,
        "discounted": 0 if starting_price == final_price else 1,
    }
    products_sklavenitis.put(new_row)


def scrape_ab():
    start_time = time.time()
    categories_df = scrape_categories_ab(
        "https://api.ab.gr/?operationName=LeftHandNavigationBar&variables={%22lang%22:%22gr%22}&extensions={%22persistedQuery%22:{%22version%22:1,%22sha256Hash%22:%2229a05b50daa7ab7686d28bf2340457e2a31e1a9e4d79db611fcee435536ee01c%22}}",
    )

    total_pages = categories_df["pages"].sum()
    completed_pages = 0
    for index, row in categories_df.iterrows():
        category = row["category"]
        pages = row["pages"]
        for page in range(0, pages - 1):
            scrape_products_ab(
                "https://www.ab.gr",
                f"https://api.ab.gr/?operationName=GetCategoryProductSearch&variables={{%22category%22:%22{category}%22,%22pageNumber%22:{page}}}&extensions={{%22persistedQuery%22:{{%22version%22:1,%22sha256Hash%22:%227666accda68452ba9b05424ad98dec3cd402eacd9b896718a0a932975a0f405a%22}}}}",
                exceptions,
            )
            completed_pages += 1
            progress = completed_pages / total_pages
            progress_bar_length = 50
            filled_length = int(progress * progress_bar_length)
            bar = "#" * filled_length + "-" * \
                (progress_bar_length - filled_length)
            print(
                f"\rScraping ΑΒ Βασιλόπουλος... [{bar}] {int(progress * 100)}%", end="")
            time.sleep(random.uniform(1, 2))

    scrape_product_exceptions_ab_recursive(exceptions)
    duration_seconds = time.time() - start_time
    minutes, seconds = divmod(duration_seconds, 60)
    print(
        f"\nScraping ΑΒ Βασιλόπουλος complete, runtime: {int(minutes)} minutes, {int(seconds)} seconds")
    return products_ab


def scrape_categories_ab(url):
    """
    Parses the categories within each store, in order to get the links to all categories.

    Parameters:
        landing_page (Literal): Indicates the landing page of a particular store.

    Returns:
        TODO
    """

    categories = pandas.DataFrame(columns=["category", "pages"])
    ignore_list = ["Νέα Προϊόντα", "Καλάθι", "κατοικίδια", "Προσφορές"]
    response = urlopen(url)
    data_json = json.loads(response.read())
    data = [item for item in data_json["data"]["leftHandNavigationBar"]
            ["levelInfo"] if not any(word in item.get("name") for word in ignore_list)]

    for entry in data:
        categories.loc[len(categories)] = [entry["code"],
                                           math.ceil(entry["productCount"] / 50)]

    return categories


def scrape_products_ab(landing_page, url, exceptions):
    """
    Iterates all pages within a category, necessary due to pagination.
    Breaks when there are no more product links provided.

    Parameters:
        TODO
        url (str): The category url that will be parsed for all its products' data to be scraped.
        products (Queue): A queue to temporarily hold the data, because of thread locking.
    """
    try:
        response = urlopen(url)
        data_json = json.loads(response.read())
        data = [item for item in data_json["data"]
                ["categoryProductSearch"]["products"]]

        for entry in data:
            price_per_unit = (
                re.sub(
                    r"(\d+),(\d) €/",
                    r"\1,\g<2>0 €/",
                    entry["price"]["discountedUnitPriceFormatted"]
                    if entry["price"]["discountedPriceFormatted"] is not None
                    and entry["price"]["discountedPriceFormatted"].replace("€", "") != entry["price"]["unitPriceFormatted"]
                    else entry["price"]["supplementaryPriceLabel1"],
                )
                .replace("Ε", "€")
                .replace("/ ", "/")
                .replace("κιλ", "κιλό")
                .replace("λιτ", "λίτρο")
                .replace("τεμ", "τεμ.")
                .replace("μεζ", "πλύση")
                .replace("kg", "κιλό")
                .replace("~", "")
            )

            product_name = entry["manufacturerName"] + \
                " " if entry["manufacturerName"] != "-" else ""

            if price_per_unit and price_per_unit != "":
                try:
                    parts = price_per_unit.strip().split()
                    price_per_unit = float(parts[0].replace(",", ".").strip())
                    metric_unit = parts[1].strip()
                except (ValueError, IndexError):
                    price_per_unit = None
                    metric_unit = None
            else:
                price_per_unit = None
                metric_unit = None

            starting_price = entry["price"]["value"]
            final_price = (
                None
                if entry["price"]["discountedPriceFormatted"] is None
                else entry["price"]["discountedPriceFormatted"].replace("€", "").replace(",", ".").replace("~", "").strip()
            )

            new_row = {
                "code": entry["code"],
                "store": "ΑΒ Βασιλόπουλος",
                "link": landing_page + entry["url"],
                "product_name": product_name + entry["name"],
                "starting_price": starting_price,
                "final_price": float(final_price),
                "price_per_unit": price_per_unit,
                "metric_unit": metric_unit,
                "discounted": 0 if not final_price or (final_price and starting_price == float(final_price)) else 1,
            }
            products_ab.put(new_row)
    except urllib.error.URLError as e:
        exceptions.append(url)


def scrape_product_exceptions_ab_recursive(exceptions):
    """ TODO """
    exceptions_new = []
    for url in exceptions:
        try:
            scrape_products_ab("https://www.ab.gr", url,
                               products_ab, exceptions_new)
        except (urllib.error.URLError, KeyError):
            exceptions.append(url)

    if exceptions_new:
        scrape_product_exceptions_ab_recursive(exceptions_new, products_ab)
