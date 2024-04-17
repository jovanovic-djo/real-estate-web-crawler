# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RealestateItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ApartmentItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    square_price = scrapy.Field()
    area = scrapy.Field()
    rooms = scrapy.Field()
    floor = scrapy.Field()
    city = scrapy.Field()
    location = scrapy.Field()
    source = scrapy.Field()