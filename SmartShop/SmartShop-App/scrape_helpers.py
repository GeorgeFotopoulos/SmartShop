import json
import math
import re
import unicodedata
import urllib
from typing import List
from urllib.request import urlopen

import pandas
import requests
from bs4 import BeautifulSoup


def scrape_categories(landing_page, categories_page) -> List[str]:
    """
    Parses the categories within each store, in order to get the links to all categories.

    Parameters:
            landing_page (Literal): Indicates the landing page of a particular store.
            categories_page (Literal): Indicates the categories page within the website.

    Returns:
            TODO
    """

    categories = []
    ignore_list = ["vrefika", "thymiamatos",
                   "katoikidia", "kava", "etoima-geymata"]
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


def scrape_products(prefix, category, products):
    """
    Iterates all pages within a category, necessary due to pagination.
    Breaks when there are no more product links provided.

    Parameters:
            prefix (Literal): The category url that contains all objects that will be scraped for data.
            category (str): A particular category that will be parsed for all its products' data to be scraped.
            products (Queue): A queue to temporarily hold the data, because of thread locking.
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
            scrape_data(prefix, products, product)

        i += 1


def scrape_data(prefix, products, product):
    """
    Scrapes product link, name, flat price and price per unit.

    Parameters:
            prefix (Literal): The prefix to add to the url for each particular product.
            products (Queue): A queue to temporarily hold the data, because of thread locking.
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
        "discounted": 0 if starting_price == final_price else 1
    }
    products.put(new_row)


def scrape_categories_ab(url):
    """
    Parses the categories within each store, in order to get the links to all categories.

    Parameters:
            landing_page (Literal): Indicates the landing page of a particular store.

    Returns:
            TODO
    """

    categories = pandas.DataFrame(columns=["category", "pages"])
    ignore_list = ["Νέα Προϊόντα", "Καλάθι", "κατοικίδια", "μωρό", "Προσφορές"]
    response = urlopen(url)
    data_json = json.loads(response.read())
    data = [item for item in data_json["data"]["leftHandNavigationBar"]
            ["levelInfo"] if not any(word in item.get("name") for word in ignore_list)]

    for entry in data:
        categories.loc[len(categories)] = [entry["code"],
                                           math.ceil(entry["productCount"] / 50)]

    return categories


def scrape_products_ab(landing_page, url, products, exceptions):
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

            if price_per_unit:
                try:
                    parts = price_per_unit.strip().split()
                    price_per_unit = float(parts[0].replace(",", ".").strip())
                    metric_unit = parts[1].strip()
                except (ValueError, IndexError):
                    price_per_unit = None
                    metric_unit = None
            else:
                price_per_unit = 0.00
                metric_unit = None

            starting_price = entry["price"]["unitPrice"]
            final_price = None if entry["price"]["discountedPriceFormatted"] is None else entry["price"]["discountedPriceFormatted"].replace(
                "€", "").replace(",", ".").replace("~", "").strip()

            new_row = {
                "code": entry["code"],
                "store": "ΑΒ Βασιλόπουλος",
                "link": landing_page + entry["url"],
                "product_name": product_name + entry["name"],
                "starting_price": starting_price,
                "final_price": float(final_price),
                "price_per_unit": price_per_unit,
                "metric_unit": metric_unit,
                "discounted": 0 if final_price is not None and starting_price == float(final_price) else 1}
            products.put(new_row)
    except urllib.error.URLError as e:
        exceptions.append(url)


def scrape_product_exceptions_ab_recursive(exceptions, products):
    """TODO"""
    exceptions_new = []
    for url in exceptions:
        try:
            scrape_products_ab("https://www.ab.gr", url,
                               products, exceptions_new)
        except (urllib.error.URLError, KeyError):
            exceptions.append(url)

    if exceptions_new:
        scrape_product_exceptions_ab_recursive(exceptions_new, products)
