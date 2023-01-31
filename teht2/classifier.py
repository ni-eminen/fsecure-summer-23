"""This script takes a URL as an argument and classifies the page pointed to by
the URL as either a gambling site or a non-gambling site."""

import sys
import pandas as pd
from helpers.preprocessing import get_texts_from_url, preprocess_text_documents, get_most_common_words

DEFAULT_GAMBLING_SITE_THRESHOLD = 0.2681992337164751

if len(sys.argv) == 1:
    print('Give a URL as the first argument.')
    print('If you want to train the classifier again, '
          'give filepath to txt file with gambling site URLs as the second argument.')
    sys.exit()

if len(sys.argv) >= 2:
    URL = sys.argv[1]

if len(sys.argv) >= 3:
    GAMBLING_SITES_TRAINING_SET_PATH = sys.argv[2]
else:
    GAMBLING_SITES_TRAINING_SET_PATH = None

common_df = pd.read_csv('./most_common_gambling_words.csv')


def retrain_classifier():
    """
    Retrains the classifier
    :return: A threshold for gambling site classifier.
    """
    try:
        with open(GAMBLING_SITES_TRAINING_SET_PATH, encoding='UTF-8') as training_set_path:
            lines = training_set_path.readlines()
            avg_similarity = 0
            errors = 0
            for line in lines:
                texts = get_texts_from_url(line)
                most_common = get_most_common_words([texts])
                if len(most_common) < 20:
                    errors += 1
                    continue
                percentage = len([x for x in most_common
                                    if x[0] in common_df['word'].values]) / len(most_common)
                avg_similarity += percentage

            avg_similarity = avg_similarity / max((len(lines) - errors), 1)
            return avg_similarity
    except EnvironmentError as error:
        print(error)
        return 0


if GAMBLING_SITES_TRAINING_SET_PATH is not None:
    GAMBLING_SITE_THRESHOLD = retrain_classifier()
else:
    # Average percentage of shared keywords for a gambling site in
    # the training set (gambling_sites.txt)
    GAMBLING_SITE_THRESHOLD = DEFAULT_GAMBLING_SITE_THRESHOLD


def classify_site(url: str, classification_threshold=GAMBLING_SITE_THRESHOLD):
    """
    Classifies a web page on whether it is a gambling site or not.
    :param url: a valid URL that points to a web page.
    :param classification_threshold: A threshold for classification.
    Defaults to an average percentage of shared keywords between the
    training gambling sites and the most common gambling keywords.
    """
    text_content = get_texts_from_url(url)

    # Could not fetch
    if text_content == '':
        sys.exit()

    processed = preprocess_text_documents([text_content])
    common_words = get_most_common_words(processed)
    percentage_of_gambling_words = len([x for x in common_words if x[0] in
                                        common_df['word'].values]) / len(common_words)

    if percentage_of_gambling_words > classification_threshold:
        print('Gambling site')
    else:
        print('Non-Gambling site')


classify_site(URL)
