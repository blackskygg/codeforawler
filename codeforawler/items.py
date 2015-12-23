# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CodeforawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ProblemItem(scrapy.Item):
    id = scrapy.Field()
    contest_id = scrapy.Field()
    title = scrapy.Field()
    tm = scrapy.Field()
    mm = scrapy.Field()
    inf = scrapy.Field()
    outf = scrapy.Field()
    content = scrapy.Field()
    inspec = scrapy.Field()
    outspec = scrapy.Field()
    in_eg = scrapy.Field()
    out_eg = scrapy.Field()
    note = scrapy.Field()

class SubmitItem(scrapy.Item):
    date = scrapy.Field()
    ppl = scrapy.Field()
    pro_id  = scrapy.Field()
    lang = scrapy.Field()
    result = scrapy.Field()
    tm = scrapy.Field()
    mm = scrapy.Field()

class ContestItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    tm = scrapy.Field()
    duration = scrapy.Field()

