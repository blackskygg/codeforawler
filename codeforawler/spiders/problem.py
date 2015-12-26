# -*- coding: utf-8 -*-
import scrapy
import redis

from codeforawler.items import ProblemItem

#these are xpaths for extracting problem infos
stm_xpath = '//div[@class="problem-statement"]'
title_xpath = stm_xpath + '/div[@class="header"]/div[@class="title"]/text()'
tm_xpath = stm_xpath + '/div[@class="header"]/div[@class="time-limit"]/text()'
mm_xpath = stm_xpath + '/div[@class="header"]/div[@class="memory-limit"]/text()'
inf_xpath = stm_xpath + '/div[@class="header"]/div[@class="input-file"]/text()'
outf_xpath = stm_xpath + '/div[@class="header"]/div[@class="output-file"]/text()'
content_xpath = stm_xpath + '/div[2]//text()'
inspec_xpath = stm_xpath + '/div[@class="input-specification"]/p//text()'
outspec_xpath = stm_xpath + '/div[@class="output-specification"]/p//text()'
ineg_xpath = stm_xpath + '/div[@class="sample-tests"]/div[@class="sample-test"]//div[@class="input"]'
outeg_xpath = stm_xpath + '/div[@class="sample-tests"]/div[@class="sample-test"]//div[@class="output"]'
note_xpath = stm_xpath + '/div[@class="note"]//p//text()'


class ProblemSpider(scrapy.Spider):
    name = "problem"
    allowed_domains = ["www.codeforces.com"]
    start_urls = []

    def __init__(self, rdhost='localhost', *args, **kwargs):
        self.rd = redis.Redis(host = rdhost)

        src, url = self.rd.blpop("problem_list")
        self.start_urls.append(url)
        super(ProblemSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        #if error occurred, add it to the err list and continue
        if response.status != 200:
            self.rd.rpush("problem_list_err", response.url)
            src, url = self.rd.blpop("problem_list")
            yield scrapy.Request(url)
            return

        #get the information, and skip those ill-formed(usually broken) pages
        item = ProblemItem()
        try:
            item['title'] = response.xpath(title_xpath).extract()[0].strip()
            item['tm'] = response.xpath(tm_xpath).extract()[0].strip()
            item['mm'] = response.xpath(mm_xpath).extract()[0].strip()
            item['inf'] = response.xpath(inf_xpath).extract()[0].strip()
            item['outf'] = response.xpath(outf_xpath).extract()[0].strip()
        except Exception:
            self.rd.rpush("problem_list_err", response.url)
            src, url = self.rd.blpop("problem_list")
            yield scrapy.Request(url)
            return

        #we can get the problem id and the contest id from the url
        url_parts = response.url.split("/")
        url_len = len(url_parts)
        item['id'] = url_parts[url_len-2] + url_parts[url_len-1]
        item['contest_id'] = url_parts[url_len-2]


        item['content'] = ""
        for s in response.xpath(content_xpath).extract():
            item['content'] += s
        item['content'] = item['content'].strip()

        item['inspec'] = ""
        for s in response.xpath(inspec_xpath).extract():
            item['inspec'] += s

        item['outspec'] = ""
        for s in response.xpath(outspec_xpath).extract():
            item['outspec'] += s
        item['outspec'] = item['outspec'].strip()

        item['note'] = ""
        for s in response.xpath(note_xpath).extract():
            item['note'] += s
        item['note'] = item['note'].strip()

        item['in_eg'] = []
        item['out_eg'] = []
        for sel1, sel2 in zip(response.xpath(ineg_xpath), response.xpath(outeg_xpath)):
            item['in_eg'].append("\n".join(sel1.xpath('pre//text()').extract()).strip())
            item['out_eg'].append("\n".join(sel2.xpath('pre//text()').extract()).strip())

        yield item

        # get more work from server
        src, url = self.rd.blpop("problem_list")
        yield scrapy.Request(url)
