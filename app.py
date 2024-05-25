import re
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import requests
from bs4 import BeautifulSoup

# Ensure necessary NLTK resources are available
from nltk.data import find
from nltk import download

try:
    find('corpora/stopwords.zip')
    find('tokenizers/punkt.zip')
    find('taggers/averaged_perceptron_tagger.zip')
except LookupError:
    download('stopwords')
    download('punkt')
    download('averaged_perceptron_tagger')

def fetch_and_clean_text(url):
    print(f"Fetching URL: {url}")
    response = requests.get(url)
    print(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        raw_text = ' '.join(element.strip() for element in soup.find_all(string=True) if element.strip())
        print(f"Raw text length: {len(raw_text)}")
        clean_text = remove_enclosed_text(raw_text)
        tokens = tokenize_and_clean(clean_text)
        print("Scraping Successful")
        return ' '.join(tokens)
    else:
        print("Failed to retrieve the webpage.")
        return "Failed"

def remove_enclosed_text(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    return text

def tokenize_and_clean(text):
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    clean_tokens = [word for word in tokens if word.lower() not in stop_words and word not in string.punctuation]
    return clean_tokens
