# -*- coding: utf-8 -*-
import scrapy
import redis
from codeforawler.items import SubmitItem

#xpaths for extracting the submission info
entry_xpath = '//table[@class="status-frame-datatable"]//tr[@data-submission-id]'

url_base = "http://www.codeforces.com/problemset/status/page/%d?order=BY_ARRIVED_DESC"

class SubmitSpider(scrapy.Spider):
    name = "submit"
    allowed_domains = ["www.codeforces.com"]
    start_urls = []
    rd = redis.Redis()

    def __init__(self, *args, **kwargs):
        index = self.rd.incr("status_index")
        self.start_urls.append(url_base % index)
        super(SubmitSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        #if error occurred, add it to the err list
        if response.status != 200:
            self.rd.rpush("submit_list_err", response.url)
            index = self.rd.incr("status_index")
            yield scrapy.Request(url_base % index)
            return


        # fill in the submit item
        item = SubmitItem()
        flag = 0
        for sel in response.xpath(entry_xpath):
            flag = 1
            item['date'] = sel.xpath('td[2]//text()').extract()[0].strip()

            item['ppl'] = ""
            for s in sel.xpath('td[3]//text()').extract():
                item['ppl'] += s
            item['ppl'] = item['ppl'].strip()

            #extracting the problem-id actually takes a little bit more work
            pro_str, item['pro_id'] = "", ""
            for s in sel.xpath('td[4]//text()').extract():
                pro_str += s
            for s in pro_str:
                if(s == '-'):
                    break
                else:
                    item['pro_id'] += s
            item['pro_id'] = item['pro_id'].strip()

            item['lang'] = sel.xpath('td[5]//text()').extract()[0].strip()

            item['result'] = ""
            for s in sel.xpath('td[6]//text()').extract():
                item['result'] += s
            item['result'] = item['result'].strip()

            item['tm'] = sel.xpath('td[7]//text()').extract()[0].strip()
            item['mm'] = sel.xpath('td[8]//text()').extract()[0].strip()

            yield item

        #if no content is selected, we reach the end
        if flag == 0:
            return

        #fetch more work from redis-db
        index = self.rd.incr("status_index")
        yield scrapy.Request(url_base % index)

