# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DatakhiItem(scrapy.Item):
    # define the fields for your item here like:
    url_image: str = scrapy.Field()
    url: str = scrapy.Field()
    name: str = scrapy.Field()

    id: str = scrapy.Field()
    color: str = scrapy.Field()
    size: list = scrapy.Field()
    composition: str = scrapy.Field()
    price: float = scrapy.Field()

    description: str = scrapy.Field()

    category: str = scrapy.Field()
    provenance: list = scrapy.Field()

    # NOT TO Display
    currency: str = scrapy.Field()
