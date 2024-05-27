import re
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import boto3
from nltk import pos_tag

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

# AWS credentials
AWS_ACCESS_KEY = '*******************'
AWS_SECRET_KEY = '***********************'
AWS_REGION = '***********'

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=AWS_ACCESS_KEY,
                          aws_secret_access_key=AWS_SECRET_KEY,
                          region_name=AWS_REGION)

# Define DynamoDB tables
website_data_table = dynamodb.Table('WebsiteData')
pos_tags_table = dynamodb.Table('WebsitePOSTags')

# Helper functions
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

def store_website_data(url, text, table):
    table.put_item(Item={'website_url': url, 'scraped_data': text})

def store_pos_tags(url, text, table):
    tokens = word_tokenize(text)
    tags = pos_tag(tokens)
    pos_tags = {word: tag for word, tag in tags if tag in ['NN', 'PRP']}
    table.put_item(Item={'website_url': url, 'pos_tags': pos_tags, 'tokens': tokens})

def retrieve_website_data(url, table):
    response = table.get_item(Key={'website_url': url})
    return response.get('Item')

def retrieve_pos_tags(url, table):
    response = table.get_item(Key={'website_url': url})
    return response.get('Item')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        url = request.json.get("url")
        text = fetch_and_clean_text(url)
        if text != "Failed":
            store_website_data(url, text, website_data_table)
            store_pos_tags(url, text, pos_tags_table)
            web_data = retrieve_website_data(url, website_data_table)
            pos_data = retrieve_pos_tags(url, pos_tags_table)
            return jsonify({'website_data': web_data, 'pos_tags': pos_data})
        else:
            return render_template("failed.html")
    except Exception as e:
        print(f"Error: {e}")
        return render_template("failed.html", error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
