#-*-coding-*-:utf8
import datetime
import random
import time

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
fileobj=open('review.txt','ab')
class ShopreviewSpider(BaseSpider):
    name = "hotel"
    allowed_domains = ["dianping.com"]
    start_urls = []
    
    handle_httpstatus_list = [404,403]

    def __init__(self):
        self._shopid = "19638508"
        self._thisyear_int = datetime.date.today().year
        self.l=[]
        fileobj=open('id.txt')
        for line in fileobj:
            self.l.append(line.strip())
        print len(self.l)
        year_g = 2014
        mon_g = 7
        max_day = 31

        self._min_date = datetime.date(year_g, mon_g, 1)
        self._max_date = datetime.date(year_g, mon_g, max_day)
        self.id=0
        #set start url
        self.pagno = 1
        self.start_urls = ["http://www.dianping.com/shop/%s/review_more?pageno=%s" % (self.l[self.id],self.pagno)]

    def parse(self, response):
        if response.status == 403:
            time.sleep(10*60)
            yield Request(response.url,callback=self.parse,
                          headers={'Referer':'http://www.baidu.com/s?psid=sdafwewer'+str(1)})
        elif response.status == 404:
            print "\n\nmeet 404, mark shop fetched and return\n\n"
        else:
            hxs = HtmlXPathSelector(response)
            #extract reviews
            good_name=hxs.select('//div[@class=\"revitew-title\"]//a/@title').extract()[0]# name 
            good_id=hxs.select('//div[@class=\"revitew-title\"]//a/@href').extract()[0].split('/')[-1]
            xs = hxs.select('//div[@class=\"comment-list\"]/ul/li')
            generate_new_request = True
            if len(xs) == 0:
                print "len(xs) == 0"
                generate_new_request = False
            for x in xs:
                reviewer = x.select('div[@class=\"pic\"]/a/img/@title').extract()[0]
                reviewer_id=x.select('div[@class=\"pic\"]/a/@user-id').extract()[0]				
                #print reviewer
                review = x.select('div[@class=\"content\"]/div[@class=\"comment-txt\"]/div[@class=\"J_brief-cont\"]/text()').extract()[0].strip()
                #print review
                s=x.select('div[@class=\"content\"]/div[@class=\"user-info\"]/div[@class=\"comment-rst\"]/span/text()').extract()
                score=""
                for i in range(len(s)):
                    score+=s[i][-1]+' '
                #print score
                review_id=x.select('div[@class=\"content\"]/div[@class=\"misc-info\"]/@id').extract()[0].split('_')[1]
                #print review_id
                appro=x.select('div[@class=\"content\"]/div[@class=\"misc-info\"]/span/span[@class=\"countWrapper\"]/a/span[@class=\"heart-num\"]/text()').extract()
                if len(appro)==0:
                    appropriate='0'
                else:
                    appropriate=str(appro[0][1])
                #print appropriate
                reviewdate_t = x.select('div[@class=\"content\"]/div[@class=\"misc-info\"]/span[@class=\"time\"]/text()').extract()[0].split()[0]
                reviewdate=""
                if len(reviewdate_t) == 5:
                    reviewdate = ("%s"%(self._thisyear_int))+"-"+reviewdate_t
                #print reviewdate
                fileobj.write(reviewdate.encode("utf8")+'\t'+review_id.encode("utf8")+'\t'+reviewer_id.encode("utf8")+'\t'+reviewer.encode("utf8")+'\t'+review.encode("utf8")+'\t'+score.encode("utf8")+'\t'+appropriate.encode("utf8")+'\t'+good_id.encode("utf8")+'\t'+good_name.encode("utf8")+'\n')
            xs = hxs.select('//a[@class=\"PageLink\"]')
            max_pages = max( [int(x.select("text()").extract()[0]) for x in xs] )
           
            if self.pagno<max_pages:
                self.pagno += 1
                new_url = "http://www.dianping.com/shop/%s/review_more?pageno=%s" % (self.l[self.id], self.pagno)
               
                rand_int = random.randint(1,999999)
                yield Request(new_url, callback=self.parse,
                                 headers={'Referer':'http://www.baidu.com/s?psid=sdafwewer'+str(rand_int)})
            else:
                self.pagno=1
                self.id+=1
                if self.id!=len(self.l):
             
                    new_url = "http://www.dianping.com/shop/%s/review_more?pageno=%s" % (self.l[self.id], self.pagno)
               
                    rand_int = random.randint(1,999999)
                    yield Request(new_url, callback=self.parse,
                                 headers={'Referer':'http://www.baidu.com/s?psid=sdafwewer'+str(rand_int)})
            
            
            
