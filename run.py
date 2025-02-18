from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from tutorial.spiders.image_spider import ImageSpider
from flask import Flask, render_template_string
import json
import threading
import webbrowser
import time

# Flask app for serving the results
app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Scraped Images</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .image-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .image-card img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }
        .image-card p {
            margin: 10px 0;
            word-break: break-all;
            font-size: 14px;
            color: #666;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .stats {
            text-align: center;
            margin-bottom: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Scraped Images</h1>
        <div class="stats">
            Total Images Found: {{ images|length }}
        </div>
        <div class="image-grid">
            {% for image in images %}
            <div class="image-card">
                <img src="{{ image.image_url }}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22200%22><rect width=%22300%22 height=%22200%22 fill=%22%23cccccc%22/><text x=%22150%22 y=%22100%22 fill=%22%23999999%22 text-anchor=%22middle%22>Image Failed to Load</text></svg>'">
                <p><strong>Source:</strong> {{ image.source_page }}</p>
                <p><strong>URL:</strong> {{ image.image_url }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
    try:
        with open("images.json", "r") as f:
            images = json.load(f)
        return render_template_string(HTML_TEMPLATE, images=images)
    except FileNotFoundError:
        return "No images found. Please run the spider first."


def run_flask():
    app.run(port=3000)


def run_spider(url):
    # Get the project settings
    settings = get_project_settings()

    # Initialize the crawler process
    process = CrawlerProcess(settings)

    # Start the spider
    process.crawl(ImageSpider, start_url=url)
    process.start()


def main():
    # Get URL from user
    url = input("Enter the website URL to scrape (e.g., https://example.com): ").strip()

    if not url:
        print("No URL provided. Exiting...")
        return

    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    print(f"Starting spider for: {url}")
    print("This may take a few minutes depending on the size of the website...")

    # Run the spider
    run_spider(url)

    print("\nSpider finished crawling!")
    print("Starting web server...")

    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Wait a moment for the server to start
    time.sleep(2)

    # Open the web browser
    print("\nOpening web interface in your browser...")
    webbrowser.open("http://localhost:3000")

    print("\nPress Ctrl+C to stop the server and exit")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
