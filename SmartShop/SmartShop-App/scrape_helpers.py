import random
import re
import time
import unicodedata
from typing import List

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Generate a random number between min_sleep and max_sleep
min_sleep = 5
max_sleep = 7
sleep_time = random.randint(min_sleep, max_sleep)


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
    response = requests.get(categories_page)
    soup = BeautifulSoup(response.text, "html.parser")
    ul_mainNav = soup.find("ul", {"class": "mainNav_ul"})
    lis = ul_mainNav.find_all("li")

    for li in lis:
        ul_mainNav_sub = li.find("ul", {"class": "mainNav_sub"})
        if ul_mainNav_sub:
            a_tags = ul_mainNav_sub.find_all("a")
            for a in a_tags:
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
        products_list = soup.find_all("div", class_=re.compile("^product prGa_"))

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

    if "sklavenitis" in prefix:
        shop = "Σκλαβενίτης"
    elif "mymarket" in prefix:
        shop = "My Market"
    else:
        shop = "ΑΒ Βασιλόπουλος"

    element = product.find("a", class_="absLink")["href"]
    if element:
        link = prefix + element

    element = product.find("h4", class_="product__title")
    if element:
        d = {ord("\N{COMBINING ACUTE ACCENT}"): None}
        product_name = unicodedata.normalize("NFD", element.text).upper().translate(d)

    element = product.find("div", class_="price")
    if element:
        flat_price = element.text

    element = product.find("div", class_="hightlight")
    if element:
        price_per_unit = element.text
    else:
        element = product.find("div", class_="priceKil")
        if element and element.text.strip():
            price_per_unit = element.text
        else:
            price_per_unit = flat_price

    new_row = {"shop": shop, "link": link, "product_name": product_name, "flat_price": flat_price.strip(), "price_per_unit": price_per_unit.strip()}
    products.put(new_row)


def scrape_categories_using_webdriver(landing_page) -> List[str]:
    """
    Parses the categories within each store, in order to get the links to all categories.\n
    Uses webdriver, because the HTML code loads after JavaScript code has ran.

    Parameters:
        landing_page (Literal): Indicates the landing page of a particular store.

    Returns:
        TODO
    """
    categories = []
    ignore_list = ["Νέα Προϊόντα", "Καλάθι", "κατοικίδια", "μωρό", "Προσφορές"]

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-site-isolation-trials")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(landing_page)
    time.sleep(sleep_time)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    a_tags = [element for element in soup.find_all("a", class_="sc-bg1agw-1 fsOPpl") if not any(word in element.text for word in ignore_list)]
    for a in a_tags:
        categories.append(landing_page + a["href"])

    driver.quit()
    return categories


def scrape_products_ab(prefix, category, products):
    """
    Iterates all pages within a category, necessary due to pagination.
    Breaks when there are no more product links provided.

    Parameters:
        prefix (Literal): The prefix to add to the url for each particular product.
        category (str): A particular category that will be parsed for all its products' data to be scraped.
        products (Queue): A queue to temporarily hold the data, because of thread locking.
    """

    html = load_and_scroll(category)
    soup = BeautifulSoup(html, "html.parser")
    products_list = soup.find_all("div", {"class": "sc-y4jrw3-2 bNyLGm"})

    for product in products_list:
        scrape_data_ab(prefix, products, product)


def scrape_data_ab(prefix, products, product):
    """
    Scrapes product link, name, flat price and price per unit.

    Parameters:
        prefix (Literal): The prefix to add to the url for each particular product.
        products (Queue): A queue to temporarily hold the data, because of thread locking.
        product (BeautifulSoup): A particular product's soup variable, to extract the data from.
    """

    shop = "ΑΒ Βασιλόπουλος"

    element = product.find("a", class_="sc-y4jrw3-6 jSkhQP")["href"]
    if element:
        link = prefix + element

    brand = product.find("a", class_="sc-y4jrw3-6 jSkhQP")
    element = product.find("a", {"data-testid": "product-block-name-link"})
    d = {ord("\N{COMBINING ACUTE ACCENT}"): None}

    if brand and brand.text.strip() not in ("", "-"):
        product_name = f"{brand.text.strip()} - {unicodedata.normalize('NFD', element.text).upper().translate(d)}"
    else:
        product_name = unicodedata.normalize("NFD", element.text).upper().translate(d)

    flat_price = None
    element = product.find("div", class_="sc-1qeaiy2-2 jRcVhQ")
    if element and element.text.strip():
        flat_price = element.text
    else:
        element = product.find("div", class_="sc-1qeaiy2-2 oTDWG")
        if element:
            flat_price = element.text

    if flat_price is None:
        return

    element = product.find("div", class_="sc-1qeaiy2-3 jtuEVK")
    if element and element.text.strip():
        price_per_unit = (
            element.text.replace("Ε", "€")
            .replace("/ ", "/")
            .replace("κιλ", "κιλό")
            .replace("λιτ", "λίτρο")
            .replace("τεμ", "τεμ.")
            .replace("μεζ", "πλύση")
            .replace("kg", "κιλό")
            .replace("~", "")
        )
        price_per_unit = re.sub(r"(\d+),(\d) €/", r"\1,\g<2>0 €/", price_per_unit)

    else:
        element = product.find("div", class_="sc-1qeaiy2-3 dqIePs")
        if element and element.text.strip():
            price_per_unit = (
                element.text.replace("Ε", "€")
                .replace("/ ", "/")
                .replace("κιλ", "κιλό")
                .replace("λιτ", "λίτρο")
                .replace("τεμ", "τεμ.")
                .replace("μεζ", "πλύση")
                .replace("kg", "κιλό")
                .replace("~", "")
            )
            price_per_unit = re.sub(r"(\d+),(\d) €/", r"\1,\g<2>0 €/", price_per_unit)

        else:
            price_per_unit = flat_price

    new_row = {"shop": shop, "link": link, "product_name": product_name, "flat_price": flat_price.strip(), "price_per_unit": price_per_unit.strip()}
    products.put(new_row)


def load_and_scroll(url):
    """TODO"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-site-isolation-trials")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(min_sleep)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

    return driver.page_source
