import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_correlations(data):
    """ TODO """
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

    # Compute the similarity matrix between the products in each store
    similarity_matrix = cosine_similarity(sklavenitis_vectors, ab_vectors)

    # Find the best match for each product in sklavenitis
    for i, row in products_sklavenitis.iterrows():
        best_match_index = np.argmax(similarity_matrix[i])
        best_match_code = products_ab.iloc[best_match_index]['code']
        correlations_dict[row['code']] = best_match_code

    return correlations_dict
