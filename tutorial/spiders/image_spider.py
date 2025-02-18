import scrapy
from scrapy.exceptions import DropItem
from urllib.parse import urlparse


class ImageURLDupeFilter:
    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        if item["image_url"] in self.seen_urls:
            # Skip this item
            raise DropItem(f"Duplicate image URL found: {item['image_url']}")
        self.seen_urls.add(item["image_url"])
        return item


# Update your spider class:
class ImageSpider(scrapy.Spider):
    name = "image_spider"

    def __init__(self, start_url=None, *args, **kwargs):
        super(ImageSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []
        if start_url:
            parsed_url = urlparse(start_url)
            self.allowed_domains = [parsed_url.netloc]
        self.seen_urls = set()  # Track seen URLs within the spider

    def parse(self, response):
        # Extract all image URLs from img tags
        img_urls = response.css("img::attr(src)").getall()

        # Extract all image URLs from background images in style attributes
        background_urls = response.css('[style*="background-image"]::attr(style)').re(
            r"url\((.*?)\)"
        )

        # Combine all found URLs
        all_urls = img_urls + background_urls

        # Clean and yield each URL
        for url in all_urls:
            # Convert relative URLs to absolute URLs
            absolute_url = response.urljoin(url.strip("'").strip('"'))

            # Skip data URLs and duplicates
            if (
                not absolute_url.startswith("data:")
                and absolute_url not in self.seen_urls
            ):
                self.seen_urls.add(absolute_url)
                yield {"image_url": absolute_url, "source_page": response.url}

        # Follow links to other pages
        for href in response.css("a::attr(href)").getall():
            if href.startswith(("http://", "https://")) or not href.startswith(
                ("tel:", "mailto:", "javascript:", "#", "data:")
            ):
                yield response.follow(href, self.parse)
