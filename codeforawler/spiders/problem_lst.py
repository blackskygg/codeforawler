# -*- coding: utf-8 -*-
import scrapy
import redis

problem_entry_xpath = '//table[@class="problems"]//tr'
url_base = "http://www.codeforces.com/problemset/page/%d"

class ProblemLstSpider(scrapy.Spider):
    name = "problem_lst"
    allowed_domains = ["www.codeforces.com"]
    start_urls = []
    rd = redis.Redis()

    def __init__(self, max_index = 26,  *args, **kwargs):
        self.max_index = max_index

        index = self.rd.incr("problemset_index")
        if index > self.max_index:
            return

        self.start_urls.append(url_base % index)
        super(ProblemLstSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        #if error occurred, add it to the err list
        if response.status != 200:
            self.rd.rpush("problem_list_err", response.url)

            index = self.rd.incr("problemset_index")
            if index > self.max_index:
                return
            else:
                yield scrapy.Request(url_base % index)
                return

        #collect the problem urls
        for sel in response.xpath(problem_entry_xpath):
            problem_url = sel.xpath('td[1]/a/@href').extract()
            if len(problem_url) == 0:
                continue
            problem_url = response.urljoin(problem_url[0])
            self.rd.rpush("problem_list", problem_url)

        #get more work from server
        index = self.rd.incr("problemset_index")
        if index > self.max_index:
            return
        else:
            yield scrapy.Request(url_base % index)
