# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProjIndeedItem(scrapy.Item):
    # define the fields for your item here like:
    jobTitle = scrapy.Field()
    CompanyName= scrapy.Field()
    jobLocation = scrapy.Field()
    Rating = scrapy.Field()
    pass
