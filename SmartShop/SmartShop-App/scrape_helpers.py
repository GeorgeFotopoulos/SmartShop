import re
import time
import unicodedata
from typing import List

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
    soup = BeautifulSoup(response.text, 'html.parser')
    ul_mainNav = soup.find('ul', {'class': 'mainNav_ul'})
    lis = ul_mainNav.find_all('li')

    for li in lis:
        ul_mainNav_sub = li.find('ul', {'class': 'mainNav_sub'})
        if ul_mainNav_sub:
            a_tags = ul_mainNav_sub.find_all('a')
            for a in a_tags:
                categories.append(landing_page+a['href'])
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
        soup = BeautifulSoup(response.content, 'html.parser')
        products_list = soup.find_all(
            'div', class_=re.compile('^product prGa_'))

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

    if 'sklavenitis' in prefix:
        shop = 'Σκλαβενίτης'
    elif 'mymarket' in prefix:
        shop = 'My Market'
    else:
        shop = 'ΑΒ Βασιλόπουλος'

    element = product.find('a', class_='absLink')['href']
    if element is not None:
        link = prefix + element

    element = product.find('h4', class_='product__title')
    if element is not None:
        d = {ord('\N{COMBINING ACUTE ACCENT}'): None}
        product_name = unicodedata.normalize(
            'NFD', element.text).upper().translate(d)

    element = product.find('div', class_='price')
    if element is not None:
        flat_price = element.text

    element = product.find('div', class_='hightlight')
    if element is not None:
        price_per_unit = element.text
    else:
        element = product.find('div', class_='priceKil')
        if element and element.text.strip():
            price_per_unit = element.text
        else:
            price_per_unit = flat_price

    new_row = {'shop': shop, 'link': link, 'product_name': product_name, 'flat_price': flat_price.strip(),
               'price_per_unit': price_per_unit.strip()}
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

    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(landing_page)
    time.sleep(5)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    ul_mainNav = soup.find('ul', {'class': 'sc-44ggw0-1 eHEjAI'})
    lis = ul_mainNav.find_all('li')
    for li in lis:
        a_tags = li.find_all('a')
        for a in a_tags:
            categories.append(landing_page+a['href'])

    driver.quit()
    return categories


def scrape_products2(prefix, category, products):
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
        chrome_options = Options()
        chrome_options.add_argument('--headless')

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(category + f"?pageNumber={i}")
        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        products_list = soup.find('ul', {'class': 'sc-y4jrw3-4 eoGbNG'})

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

    if 'sklavenitis' in prefix:
        shop = 'Σκλαβενίτης'
    elif 'mymarket' in prefix:
        shop = 'My Market'
    else:
        shop = 'ΑΒ Βασιλόπουλος'

    element = product.find('a', class_='absLink')['href']
    if element is not None:
        link = prefix + element

    element = product.find('h4', class_='product__title')
    if element is not None:
        d = {ord('\N{COMBINING ACUTE ACCENT}'): None}
        product_name = unicodedata.normalize(
            'NFD', element.text).upper().translate(d)

    element = product.find('div', class_='price')
    if element is not None:
        flat_price = element.text

    element = product.find('div', class_='hightlight')
    if element is not None:
        price_per_unit = element.text
    else:
        element = product.find('div', class_='priceKil')
        if element and element.text.strip():
            price_per_unit = element.text
        else:
            price_per_unit = flat_price

    new_row = {'shop': shop, 'link': link, 'product_name': product_name, 'flat_price': flat_price.strip(),
               'price_per_unit': price_per_unit.strip()}
    products.put(new_row)
