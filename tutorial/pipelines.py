# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class TutorialPipeline:
    def process_item(self, item, spider):
        return item


class DuplicateImagePipeline:
    def __init__(self):
        self.image_urls_seen = set()

    def process_item(self, item, spider):
        if item["image_url"] in self.image_urls_seen:
            raise DropItem(f"Duplicate item found: {item}")
        self.image_urls_seen.add(item["image_url"])
        return item
