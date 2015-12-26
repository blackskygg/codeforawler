# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import cymysql
from codeforawler.items import ContestItem, SubmitItem, ProblemItem

class SQLPipeline(object):
    contest_str = """
    insert into contest_tbl(id, name, tm, duration)
    values("%s", "%s", "%s", "%s")
    """
    submit_str = """
    insert into submit_tbl(date, ppl, pro_id, lang, result, tm, mm)
    values("%s", "%s", "%s", "%s", "%s", "%s", "%s")
    """

    problem_str = """
    insert into problem_tbl(id, contest_id, title, tm, mm, inf, outf, content,
    inspec, outspec, note)
    values("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s",
    "%s", "%s", "%s")
    """

    example_str = """
    insert into example_tbl(pro_id, in_eg, out_eg)
    values("%s", "%s", "%s")
    """


    #once reach this value, a commit will be performed
    max_record = 100

    def __init__(self, *args, **kwargs):
        self.processor_tbl = {SubmitItem : self.process_submit,
                         ContestItem : self.process_contest,
                         ProblemItem : self.process_problem}
        super(SQLPipeline, self).__init__(*args, **kwargs)

    def open_spider(self, spider):
        self.conn = cymysql.connect(host='localhost', user='sky',
                                    passwd='sherlock', db='learnsql',
                                    charset='utf8')
        self.cur = self.conn.cursor()
        self.ncontest = 0
        self.nproblem = 0
        self.nsubmit = 0
        self.nexample = 0

    def check_if_submit(self, curr):
        curr += 1
        if(curr > self.max_record):
            self.conn.commit()
            curr = 0

        return curr

    def process_contest(self, item):
        self.cur.execute(
            self.contest_str%(item['id'], item['name'],
                              item['tm'], item['duration'])
        )
        self.ncontest = self.check_if_submit(self.ncontest)

    def process_problem(self, item):
        self.cur.execute(
            self.problem_str%(item['id'], item['contest_id'],
                              item['title'], item['tm'],
                              item['mm'], item['inf'],
                              item['outf'], item['content'],
                              item['inspec'], item['outspec'], item['note'])
        )
        self.nproblem = self.check_if_submit(self.nproblem)

        for in_eg, out_eg in zip(item['in_eg'], item['out_eg']):
            self.cur.execute(
                self.example_str%(item['id'], in_eg, out_eg)
            )
            self.nexample = self.check_if_submit(self.nexample)

    def process_submit(self, item):
        self.cur.execute(
            self.submit_str%(item['date'], item['ppl'],
                             item['pro_id'], item['lang'],
                             item['result'], item['tm'], item['mm'])
        )
        self.nsubmit = self.check_if_submit(self.nsubmit)

    def process_item(self, item, spider):
        #first convert those unicode strings into escape strings
        for key, value in item.items():
            if isinstance(value, unicode):
                item[key] = cymysql.escape_string(value)

        self.processor_tbl[type(item)](item)

        return item

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
