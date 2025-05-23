from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import datetime
import logging

app = Flask(__name__)
# Configure logging to see messages in Render logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def home():
    return "Dynamic Schema Generator API is running!"

@app.route('/generate-schema', methods=['POST'])
def generate_schema():
    url = request.json.get('url')
    schema_type = request.json.get('schemaType')

    if not url or not schema_type:
        logger.warning("Missing URL or schemaType in request.")
        return jsonify({"error": "Missing URL or schemaType"}), 400

    headers = {
        # Using a more recent Chrome User-Agent
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    logger.info(f"Attempting to fetch URL: {url} for schema type: {schema_type}")

    try:
        # Added timeout to prevent requests from hanging indefinitely
        response = requests.get(url, headers=headers, timeout=10)

        # Check for non-200 status codes
        if response.status_code != 200:
            logger.error(f"Failed to fetch page for URL: {url}. Status code: {response.status_code}")
            return jsonify({"error": f"Failed to fetch page: {response.status_code}"}), 500

        logger.info(f"Successfully fetched URL: {url} with status {response.status_code}")

        # Use 'lxml' parser for potentially better performance and robustness
        soup = BeautifulSoup(response.text, 'lxml')

        # --- Extract Title ---
        title_tag = soup.find('title')
        # Ensure title_tag and its string content exist before stripping
        title = title_tag.string.strip() if title_tag and title_tag.string else 'Not Available'
        logger.info(f"Extracted title: '{title}'")

        # --- Extract Meta Description ---
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        # Ensure meta_desc_tag exists and has a 'content' attribute before accessing
        description = meta_desc_tag['content'].strip() if meta_desc_tag and 'content' in meta_desc_tag.attrs else 'Not Available'
        logger.info(f"Extracted description: '{description}'")

        # Parse the URL to get domain for relative paths and default values
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # --- Schema Generation Logic (remains largely the same) ---
        if schema_type == 'Organization':
            logo = soup.find('link', rel='icon')
            logo_url = urljoin(domain, logo['href']) if logo and logo.get('href') else 'Not Available'
            # Note: The social link extraction for 'youtube.com' seems like a typo.
            # You might want to adjust it to 'youtube.com' or similar.
            social_links = [a['href'] for a in soup.find_all('a', href=True) if any(x in a['href'] for x in ['linkedin.com', 'twitter.com', 'facebook.com', 'youtube.com'])] or ['Not Available']
            schema = {
                "@context": "https://schema.org",
                "@type": "Organization",
                "url": url,
                "name": title,
                "description": description,
                "logo": logo_url,
                "sameAs": social_links
            }

        elif schema_type == 'WebPage':
            schema = {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": title,
                "description": description,
                "url": url,
                "inLanguage": "en-US",
                "dateModified": datetime.datetime.now().isoformat(),
                "speakable": {
                    "@type": "SpeakableSpecification",
                    "cssSelector": ["title", "meta[name='description']"]
                }
            }

        elif schema_type == 'BlogPosting':
            schema = {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": title,
                "description": description,
                "url": url,
                "author": {
                    "@type": "Organization",
                    "name": parsed_url.netloc or 'Not Available'
                },
                "publisher": {
                    "@type": "Organization",
                    "name": parsed_url.netloc or 'Not Available',
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://www.example.com/logo.png" # Placeholder
                    }
                },
                "datePublished": datetime.datetime.now().isoformat(),
                "mainEntityOfPage": url
            }

        elif schema_type == 'Event':
            schema = {
                "@context": "https://schema.org",
                "@type": "Event",
                "name": title,
                "description": description,
                "startDate": "2025-03-17T09:00:00-05:00", # Placeholder
                "endDate": "2025-03-19T17:00:00-05:00",   # Placeholder
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "eventStatus": "https://schema.org/EventScheduled",
                "location": {
                    "@type": "Place",
                    "name": "JW Marriott Orlando Grande Lakes", # Placeholder
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": "4040 Central Florida Pkwy", # Placeholder
                        "addressLocality": "Orlando",
                        "addressRegion": "FL",
                        "postalCode": "32837",
                        "addressCountry": "US"
                    }
                }
            }

        elif schema_type == 'BreadcrumbList':
            schema = {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Home",
                        "item": domain
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": title,
                        "item": url
                    }
                ]
            }

        elif schema_type == 'ClaimReview':
            schema = {
                "@context": "https://schema.org",
                "@type": "ClaimReview",
                "url": url,
                "claimReviewed": title,
                "author": {
                    "@type": "Organization",
                    "name": parsed_url.netloc or 'Not Available'
                },
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": 5, # Placeholder
                    "bestRating": 5,
                    "worstRating": 1,
                    "alternateName": "True"
                }
            }

        elif schema_type == 'FAQPage':
            schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "Sample question?", # Placeholder
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Sample answer." # Placeholder
                        }
                    }
                ]
            }

        elif schema_type == 'ImageObject':
            img = soup.find('img')
            schema = {
                "@context": "https://schema.org",
                "@type": "ImageObject",
                "contentUrl": urljoin(domain, img['src']) if img and img.get('src') else 'Not Available',
                "license": url,
                "creditText": parsed_url.netloc,
                "creator": {
                    "@type": "Person",
                    "name": "Unknown" # Placeholder
                },
                "copyrightNotice": "Copyright Holder" # Placeholder
            }

        elif schema_type == 'Product':
            schema = {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": title,
                "description": description,
                "review": { # Placeholder
                    "@type": "Review",
                    "reviewRating": {
                        "@type": "Rating",
                        "ratingValue": 4,
                        "bestRating": 5
                    },
                    "author": {
                        "@type": "Person",
                        "name": "Sample User"
                    }
                },
                "aggregateRating": { # Placeholder
                    "@type": "AggregateRating",
                    "ratingValue": 4.4,
                    "reviewCount": 89
                }
            }

        elif schema_type == 'ProfilePage':
            schema = {
                "@context": "https://schema.org",
                "@type": "ProfilePage",
                "dateCreated": datetime.datetime.now().isoformat(),
                "dateModified": datetime.datetime.now().isoformat(),
                "mainEntity": {
                    "@type": "Person",
                    "name": title,
                    "identifier": "123456", # Placeholder
                    "description": description
                }
            }

        elif schema_type == 'VideoObject':
            schema = {
                "@context": "https://schema.org",
                "@type": "VideoObject",
                "name": title,
                "description": description,
                "thumbnailUrl": ["https://example.com/thumbnail.jpg"], # Placeholder
                "uploadDate": datetime.datetime.now().isoformat(),
                "duration": "PT1M30S", # Placeholder
                "contentUrl": url,
                "embedUrl": url,
                "regionsAllowed": ["US"] # Placeholder
            }

        else:
            logger.warning(f"Unsupported schemaType requested: {schema_type}")
            return jsonify({"error": f"Unsupported schemaType: {schema_type}"}), 400

        return jsonify(schema)

    except requests.exceptions.Timeout:
        logger.error(f"Request timed out for URL: {url}")
        return jsonify({"error": "Request to target URL timed out."}), 504 # Gateway Timeout
    except requests.exceptions.RequestException as e:
        status_code = getattr(e.response, 'status_code', 500) # Get status code if available
        logger.error(f"Request failed for {url} with status {status_code}: {e}")
        return jsonify({"error": f"Failed to fetch URL ({status_code}): {str(e)}"}), status_code
    except Exception as e:
        logger.exception(f"An unexpected error occurred while processing {url}:") # Use exception for full traceback
        return jsonify({"error": f"An unexpected server error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # When running locally for development
    app.run(debug=True, port=5000) # You can specify a port