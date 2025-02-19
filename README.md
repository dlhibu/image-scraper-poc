# Image Scraping with Scrapy POC
This is a very rudimentary POC that allows scraping of images from all pages on a site. To start, set up a python virtual env and install scrapy. Once this is finished, run the project with a command like "scrapy crawl image_spider -a start_url="https://example.com" -O images.json" Then, use "python run.py" to open a small website on port 3000 that allows you to preview all the images that scrapy was able to get. 

This project was created using scrapy's tutorial project. The actual "POC" code is in the "image_spider.py" file.
