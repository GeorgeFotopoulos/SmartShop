import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import KNeighborsClassifier


def get_correlations_sklavenitis(data):
    """
    Given a pandas DataFrame `data` containing product data from two stores, returns a dictionary
    that holds items from the store 'Σκλαβενίτης' with the item from the store 'ΑΒ Βασιλόπουλος'
    that has the highest correspondence.

    Args:
    - data: a pandas DataFrame containing the following columns:
      - 'store': a string indicating the store where the product was found
      - 'code': a string identifier for the product
      - 'product_name': a string containing the name of the product

    Returns:
    A dictionary mapping 'code' values from products_ab to the 'code' values from the
    corresponding best matching item in products_sklavenitis.
    """
    products_sklavenitis = data[data['store'] == 'Σκλαβενίτης']
    products_ab = data[data['store'] == 'ΑΒ Βασιλόπουλος']

    # Create a dictionary to store the product correlations
    correlations_dict = {}

    # Create a TF-IDF vectorizer to convert the product names into vectors
    vectorizer = TfidfVectorizer()

    # Fit the vectorizer to the product names in the dataset
    vectorizer.fit(data['product_name'])

    # Convert the product names in each store into TF-IDF vectors
    sklavenitis_vectors = vectorizer.transform(
        products_sklavenitis['product_name'])
    ab_vectors = vectorizer.transform(products_ab['product_name'])

    # Train a k-NN classifier on the similarity matrix
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(ab_vectors, products_ab['code'])

    # Find the best match for each product in sklavenitis
    for i, row in products_sklavenitis.iterrows():
        sklavenitis_vector = vectorizer.transform([row['product_name']])
        best_match_code = knn.predict(sklavenitis_vector)[0]
        correlations_dict[row['code']] = best_match_code

    return correlations_dict


def get_correlations_ab(data):
    """
    Given a pandas DataFrame `data` containing product data from two stores, returns a dictionary
    that holds items from the store 'ΑΒ Βασιλόπουλος' with the item from the store 'Σκλαβενίτης'
    that has the highest correspondence.

    Args:
    - data: a pandas DataFrame containing the following columns:
      - 'store': a string indicating the store where the product was found
      - 'code': a string identifier for the product
      - 'product_name': a string containing the name of the product

    Returns:
    A dictionary mapping 'code' values from products_ab to the 'code' values from the
    corresponding best matching item in products_sklavenitis.
    """
    products_ab = data[data['store'] == 'ΑΒ Βασιλόπουλος']
    products_sklavenitis = data[data['store'] == 'Σκλαβενίτης']

    # Create a dictionary to store the product correlations
    correlations_dict = {}

    # Create a TF-IDF vectorizer to convert the product names into vectors
    vectorizer = TfidfVectorizer()

    # Fit the vectorizer to the product names in the dataset
    vectorizer.fit(data['product_name'])

    # Convert the product names in each store into TF-IDF vectors
    ab_vectors = vectorizer.transform(products_ab['product_name'])
    sklavenitis_vectors = vectorizer.transform(
        products_sklavenitis['product_name'])

    # Train a k-NN classifier on the similarity matrix
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(sklavenitis_vectors, products_sklavenitis['code'])

    # Find the best match for each product in ab
    for i, row in products_ab.iterrows():
        ab_vector = vectorizer.transform([row['product_name']])
        best_match_code = knn.predict(ab_vector)[0]
        correlations_dict[row['code']] = best_match_code

    return correlations_dict


def get_correlations(data):
    sklavenitis_dict = get_correlations_sklavenitis(data)
    ab_dict = get_correlations_ab(data)
    sklavenitis_dict.update(ab_dict)
    return sklavenitis_dict
