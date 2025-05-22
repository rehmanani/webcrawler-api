from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Web Crawler API is running!"

@app.route('/generate-schema', methods=['POST'])
def generate_schema():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string.strip() if soup.title else ''
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'].strip() if meta_desc else ''

        schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "url": url,
            "name": title,
            "description": description
        }

        return jsonify(schema)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
