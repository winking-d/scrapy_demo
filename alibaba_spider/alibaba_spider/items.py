# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AlibabaSpiderItem(scrapy.Item):
    title = scrapy.Field()
    buyers = scrapy.Field()
    company_name = scrapy.Field()
    product_id = scrapy.Field()
    product_url = scrapy.Field()