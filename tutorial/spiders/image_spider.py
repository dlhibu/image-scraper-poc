import scrapy
from urllib.parse import urlparse
import re
import base64
# scrapy crawl image_spider -a start_url="https://example.com" -O images.json


class ImageSpider(scrapy.Spider):
    name = "image_spider"

    def __init__(self, start_url=None, *args, **kwargs):
        super(ImageSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []
        if start_url:
            parsed_url = urlparse(start_url)
            self.allowed_domains = [parsed_url.netloc]
        self.seen_urls = set()
        self.seen_svgs = set()

    def extract_css_urls(self, text):
        css_url_pattern = r'url\(["\']?((?!data:)[^)"\']+)["\']?\)'
        return re.findall(css_url_pattern, text)

    def extract_inline_svg(self, response):
        svg_elements = response.xpath("//svg")
        svgs = []
        for svg in svg_elements:
            svg_content = svg.get()
            if svg_content and svg_content not in self.seen_svgs:
                self.seen_svgs.add(svg_content)
                # Create a data URL for the SVG to maintain consistency with URL-based images
                svg_base64 = base64.b64encode(svg_content.encode("utf-8")).decode(
                    "utf-8"
                )
                svg_data_url = f"data:image/svg+xml;base64,{svg_base64}"
                svgs.append(
                    {
                        "image_url": svg_data_url,
                        "source_page": response.url,
                        "type": "inline_svg",
                        "original_content": svg_content,
                    }
                )
        return svgs

    def extract_css_images(self, response):
        style_tags = response.xpath("//style/text()").getall()
        urls = []
        for style in style_tags:
            urls.extend(self.extract_css_urls(style))

        style_attrs = response.xpath("//@style").getall()
        for style_attr in style_attrs:
            urls.extend(self.extract_css_urls(style_attr))

        background_elements = response.css('[style*="background"]')
        for element in background_elements:
            style = element.attrib.get("style", "")
            urls.extend(self.extract_css_urls(style))

        return urls

    def extract_linked_stylesheets(self, response):
        stylesheet_links = response.css('link[rel="stylesheet"]::attr(href)').getall()
        return stylesheet_links

    def parse_stylesheet(self, response):
        css_content = response.text
        urls = self.extract_css_urls(css_content)
        for url in urls:
            absolute_url = response.urljoin(url.strip("'").strip('"'))
            identifier = f"{absolute_url}_css_image"
            if identifier not in self.seen_urls:
                self.seen_urls.add(identifier)
                yield {
                    "image_url": absolute_url,
                    "source_page": response.url,
                    "type": "css_image",
                }

    def parse(self, response):
        # 1. Extract standard img tag sources
        for img in response.css("img"):
            src = img.attrib.get("src", "")
            srcset = img.attrib.get("srcset", "")

            if src and not src.startswith("data:"):
                absolute_url = response.urljoin(src)
                identifier = f"{absolute_url}_standard_image"
                if identifier not in self.seen_urls:
                    self.seen_urls.add(identifier)
                    yield {
                        "image_url": absolute_url,
                        "source_page": response.url,
                        "type": "standard_image",
                        "alt_text": img.attrib.get("alt", ""),
                        "dimensions": {
                            "width": img.attrib.get("width", ""),
                            "height": img.attrib.get("height", ""),
                        },
                    }

            if srcset:
                srcset_urls = [url.strip().split(" ")[0] for url in srcset.split(",")]
                for url in srcset_urls:
                    if not url.startswith("data:"):
                        absolute_url = response.urljoin(url)
                        identifier = f"{absolute_url}_srcset_image"
                        if identifier not in self.seen_urls:
                            self.seen_urls.add(identifier)
                            yield {
                                "image_url": absolute_url,
                                "source_page": response.url,
                                "type": "srcset_image",
                            }

        # 2. Extract CSS background images
        css_urls = self.extract_css_images(response)
        for url in css_urls:
            absolute_url = response.urljoin(url.strip("'").strip('"'))
            identifier = f"{absolute_url}_css_image"
            if identifier not in self.seen_urls:
                self.seen_urls.add(identifier)
                yield {
                    "image_url": absolute_url,
                    "source_page": response.url,
                    "type": "css_image",
                }

        # 3. Extract inline SVGs
        svg_elements = self.extract_inline_svg(response)
        for svg in svg_elements:
            yield svg

        # 4. Follow and parse external stylesheets
        stylesheet_links = self.extract_linked_stylesheets(response)
        for href in stylesheet_links:
            if href:
                yield response.follow(href, self.parse_stylesheet)

        # 5. Extract picture element sources
        for picture in response.css("picture"):
            sources = picture.css("source")
            for source in sources:
                srcset = source.attrib.get("srcset", "")
                if srcset:
                    srcset_urls = [
                        url.strip().split(" ")[0] for url in srcset.split(",")
                    ]
                    for url in srcset_urls:
                        if not url.startswith("data:"):
                            absolute_url = response.urljoin(url)
                            identifier = f"{absolute_url}_picture_source"
                            if identifier not in self.seen_urls:
                                self.seen_urls.add(identifier)
                                yield {
                                    "image_url": absolute_url,
                                    "source_page": response.url,
                                    "type": "picture_source",
                                    "media": source.attrib.get("media", ""),
                                    "mime_type": source.attrib.get("type", ""),
                                }

        # Follow links to other pages
        for href in response.css("a::attr(href)").getall():
            if href.startswith(("http://", "https://")) or not href.startswith(
                ("tel:", "mailto:", "javascript:", "#", "data:")
            ):
                yield response.follow(href, self.parse)
