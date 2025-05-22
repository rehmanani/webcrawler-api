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
            "Accept": "application/json"
        }

        resp = requests.post(api_url, json={"url": url}, headers=headers, timeout=10)

        if resp.status_code != 200:
            return jsonify({"error": f"Metadata fetch failed: {resp.status_code}"}), 500

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
