"""This script generates the most common words for a set of html pages
pointed to by URLs in gambling_sites.txt. The words are then saved to
file to the current working directory."""

from collections import Counter
import pandas as pd
from helpers.preprocessing import get_texts_from_url, preprocess_text_documents, flatten

# Read gambling site URLs
with open('gambling_sites.txt', encoding='UTF-8') as f:
    lines = [link.strip('\n') for link in f.readlines()]

# Create a list of the text contents on each page
gambling_texts = []
for link in lines:
    text_content = get_texts_from_url(link)
    gambling_texts.append(text_content)

# Insert into pd.DataFrame for easier processing and persisting
gambling_df = pd.DataFrame()
gambling_df['text_data'] = preprocess_text_documents(gambling_texts)

# Create a counter object for the most common words
counter = Counter(flatten(gambling_df['text_data'].apply(lambda x: x.split(' ')).values))

# Save the 150 most common words to file as CSV
common_df = pd.DataFrame()
common_df[['word', 'count']] = counter.most_common(150)
common_df.to_csv('./most_common_gambling_words.csv')
