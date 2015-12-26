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

    def __init__(self, max_index = 26, rdhost='localhost', *args, **kwargs):
        self.rd = redis.Redis(host = rdhost)
        self.max_index = max_index

        #the latest contest id  we have
        self.latest_id = self.rd.get("contest_latest_id");

        #check the stop sign
        if self.rd.get("problemset_stop"):
            return

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

            #extract the contest id and see if we've already crawled it
            url_parts = problem_url.split("/")
            url_len = len(url_parts)
            contest_id = url_parts[url_len-2]
            if contest_id <= self.latest_id:
                self.rd.set("problem_stop", "1")
                return

            self.rd.rpush("problem_list", problem_url)

        #get more work from server
        index = self.rd.incr("problemset_index")
        if index > self.max_index:
            return
        else:
            yield scrapy.Request(url_base % index)
