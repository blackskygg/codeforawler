# -*- coding: utf-8 -*-
import scrapy
import redis

from codeforawler.items import ContestItem

contest_entry_xpath = '//div[@class="contests-table"]//table//tr[@data-contestid]'
url_base = "http://www.codeforces.com/contests/page/%d"

class ContestSpider(scrapy.Spider):
    name = "contest"
    allowed_domains = ["www.codeforces.com"]
    start_urls = []

    def __init__(self, max_index = 6, rdhost='localhost', *args, **kwargs):
        self.max_index = max_index
        self.rd = redis.Redis(host = rdhost)

        #the latest contest id  we have
        self.latest_id = self.rd.get("contest_latest_id");

        #check the stop sign
        if self.rd.get("contest_stop"):
            return

        index = self.rd.incr("contests_index")
        if index > self.max_index:
            return

        self.start_urls.append(url_base % index)
        super(ContestSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        #if error occurred, add it to the err list
        if response.status != 200:
            self.rd.rpush("contest_list_err", response.url)

            index = self.rd.incr("contests_index")
            if index > self.max_index:
                return
            else:
                yield scrapy.Request(url_base % index)
                return

        item = ContestItem()
        #collect the contests' info
        for sel in response.xpath(contest_entry_xpath):
            item['id'] = sel.xpath("@data-contestid").extract()[0]
            item['name'] = sel.xpath("td[1]/text()").extract()[0].strip()
            item['tm'] = sel.xpath("td[3]/span/text()").extract()[0].strip()
            item['duration'] = sel.xpath("td[4]/text()").extract()[0].strip()

            #check if we need to crawl older info
            if int(item['id']) <= self.latest_id:
                self.rd.set("contest_stop", "1")
                return

            yield item

        #get more work from server
        index = self.rd.incr("contests_index")
        if index > self.max_index:
            return
        else:
            yield scrapy.Request(url_base % index)
