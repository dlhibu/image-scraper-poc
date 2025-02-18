# Scrapy settings for tutorial project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#

SPIDER_MODULES = ["tutorial.spiders"]
NEWSPIDER_MODULE = "tutorial.spiders"
ITEM_PIPELINES = {
    "tutorial.pipelines.DuplicateImagePipeline": 300,
}

# Add a realistic user agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Add a delay between requests
DOWNLOAD_DELAY = 1

BOT_NAME = "tutorial"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "tutorial (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

DEPTH_LIMIT = 2
