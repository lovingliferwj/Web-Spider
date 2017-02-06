#-*-coding-*-:utf8
import datetime
import random
import time

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
output=open('sanxing.txt','w')
class ShopreviewSpider(BaseSpider):
    name = "sanxing"
    allowed_domains = ["m.jd.com"]
    start_urls = []
    
    handle_httpstatus_list = [404,403]

    def __init__(self):
        self.pageno=0
        self.start_urls = ['http://item.m.jd.com/ware/comments.json?wareId=1138529&score=&sid=d5d08a7af9d3a6c0a1d5ea81df5c1a13&page=%s'%self.pageno]

    def parse(self, response):
        if response.status == 403:
            time.sleep(10*60)
            yield Request(response.url,callback=self.parse,
                          headers={'Referer':'http://www.baidu.com/s?psid=sdafwewer'+str(1)})
        elif response.status == 404:
            print "\n\nmeet 404, mark shop fetched and return\n\n"
        else:
            output.write(response.body)
            output.write('\n')
            self.pageno+=1
            if self.pageno<=800:
                new_url = 'http://item.m.jd.com/ware/comments.json?wareId=1138529&score=&sid=d5d08a7af9d3a6c0a1d5ea81df5c1a13&page=%s'%self.pageno
                rand_int = random.randint(1,999999)
                yield Request(new_url, callback=self.parse,headers={'Referer':'http://www.baidu.com/s?psid=sdafwewer'+str(rand_int)})
            
            
            
