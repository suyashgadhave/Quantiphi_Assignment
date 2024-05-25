from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import boto3
from app import fetch_and_clean_text
from nltk import pos_tag
from nltk.tokenize import word_tokenize

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        dynamodb = boto3.resource('dynamodb')
        website_data_table = dynamodb.Table('WebsiteData')
        pos_tags_table = dynamodb.Table('WebsitePOSTags')
        url = request.json.get("url")
        
        text = fetch_and_clean_text(url)
        if text != "Failed":
            store_website_data(url, text, website_data_table)
            store_pos_tags(url, text, pos_tags_table)
            web_data = retrieve_website_data(url, website_data_table)
            pos_data = retrieve_pos_tags(url, pos_tags_table)
            return jsonify({'website_data': web_data, 'pos_tags': pos_data})
        else:
            return render_template("FailedIndex.html")
    except Exception as e:
        print(f"Error: {e}")
        return render_template("FailedIndex.html", error=str(e))

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

if __name__ == '__main__':
    app.run(debug=True)
