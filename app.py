from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Web Crawler API using jsonlink.io is running!"

@app.route('/generate-schema', methods=['POST'])
def generate_schema():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        api_url = "https://jsonlink.io/api/extract"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://webcrawler-api.onrender.com",
            "Origin": "https://webcrawler-api.onrender.com"
        }

        payload = {
            "url": url
        }

        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)

        if resp.status_code != 200:
            return jsonify({"error": f"Metadata fetch failed: {resp.status_code}", "response": resp.text}), 500

        data = resp.json()

        schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "url": url,
            "name": data.get("title", ""),
            "description": data.get("description", "")
        }

        return jsonify(schema)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
