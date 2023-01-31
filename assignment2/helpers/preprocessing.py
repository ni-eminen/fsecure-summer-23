"""This is a module for shared functions of the gambling site classifier."""

from collections import Counter
import nltk
from bs4 import BeautifulSoup, Comment
from nltk import word_tokenize, WordNetLemmatizer
from nltk.corpus import stopwords
import requests


# https://stackoverflow.com/questions/1936466/how-to-scrape-only-visible-webpage-text-with-beautifulsoup
def tag_visible(element):
    """
    Determines whether an element is visible or not.
    :param element: An HTML element
    :return: True if visible, False otherwise.
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


# https://stackoverflow.com/questions/1936466/how-to-scrape-only-visible-webpage-text-with-beautifulsoup
def text_from_html(body):
    """
    Gets all the visible text from an HTML document.
    :param body: An HTML document.
    :return: All the visible text joined with a space character in between.
    """
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return " ".join(t.strip() for t in visible_texts)


def flatten(arr: list):
    """
    Flattens an array
    :param arr: An array of arrays
    :return: The arras flattened to a single array.
    """
    flattened_arr = []
    for i in arr:
        if isinstance(i, list):
            flattened_arr.extend(flatten(i))
        else:
            flattened_arr.append(i)
    return flattened_arr


def remove_special_chars(string: str):
    """
    Removes special characters from string
    :param string: string
    :return: string stripped from its special characters and leading/trailing whitespace.
    """
    return ''.join(c for c in string if c.isalnum() or c == ' ').strip()


def lemmatize_word_arr(arr: list[str], lemmatizer: nltk.WordNetLemmatizer):
    """
    Lemmatizes an array of words.
    :param arr: Array of words.
    :param lemmatizer: Preferred lemmatizer, defaults to nltk's WordNetLemmatizer.
    :return: A new array with lemmatized words.
    """
    lemmatized_arr = []
    for word in arr:
        lemmatized = lemmatizer.lemmatize(word)
        lemmatized_arr.append(lemmatized)

    return lemmatized_arr


def preprocess_text_documents(docs: list[str]):
    """
    Lemmatizes words and removes stopwords from an array of strings.
    :param docs: Text documents. An array of strings.
    :return: A new array of preprocessed strings.
    """
    lemmatizer = WordNetLemmatizer()
    tokenized = [word_tokenize(text) for text in docs]
    lemmatized = [lemmatize_word_arr(word_arr, lemmatizer) for word_arr in tokenized]
    stopwords_removed_joined = []
    for word_arr in lemmatized:
        stop_words_removed = [word for word in word_arr
                              if not word.lower() in stopwords.words('english')]
        stopwords_removed_joined.append(' '.join(stop_words_removed))

    return stopwords_removed_joined


def get_texts_from_url(url: str):
    """
    Gets all the visible text from a web page pointed to by URL.
    :param url: URL of a web page.
    :return: The visible text content on the page.
    """
    try:
        res = requests.get(url, timeout=10)
        if str(res.status_code) != '200':
            print(f'could not fetch html from {url}status code: ', res.status_code)
            return ''

        text_content = text_from_html(res.text).lower()
        text_content = remove_special_chars(text_content)
        return text_content
    except requests.exceptions.RequestException as exception:
        print(exception)
        return ''



def get_most_common_words(string_arr: str, num_of_keywords=150, delim=' '):
    """
    Returns the most common words in an array of strings.
    :param string_arr: An array of strings.
    :param num_of_keywords: Upper limit to how many of the most common strings are returned.
    :param delim: A delimiter for the words. Defaults to space character.
    :return: Up to num_of_keywords of the most common words.
    """
    word_arr = flatten([string.split(delim) for string in string_arr])
    counter = Counter(word_arr)
    return counter.most_common(num_of_keywords)
