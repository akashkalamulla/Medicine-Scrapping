# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class MedexScraperItem(scrapy.Item):
    medicine_name = scrapy.Field()
    strength = scrapy.Field()
    nutrition_info = scrapy.Field()
    manufacturer = scrapy.Field()
    unit_price = scrapy.Field()
