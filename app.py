from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# LinkPreview API Key
LINK_PREVIEW_API_KEY = "4e621422cae3dbbe91a9199d4370a465"

@app.route('/')
def home():
    return "Web Crawler API using LinkPreview is running!"

@app.route('/generate-schema', methods=['POST'])
def generate_schema():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        api_url = f"https://api.linkpreview.net/?key={LINK_PREVIEW_API_KEY}&q={url}"
        resp = requests.get(api_url, timeout=10)

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
