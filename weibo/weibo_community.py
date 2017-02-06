#-*-coding:utf8-*-
#程序主要用来获取谣言的rid  http://service.account.weibo.com
import requests
import re
from lxml import etree
from bs4 import BeautifulSoup as bs
import logging
import sys
cook = {"Cookie": "SINAGLOBAL=8610575173515.826.1418966852179; un=renwenjinghit@163.com; wvr=6; SCF=AmVg27mQiax4VUhjvjEiFndoq1U9eKJhZxHGCthIGZ_q02Hx4nWFyWzgvdIiWnrKGjQwPucI6ywK34gWLeMvcVc.; SUB=_2A2565jilDeTxGeNN6VAT8yfFzT-IHXVZki1trDV8PUNbmtBeLXD3kW9dqi7jgidB4efwqh6UjltEsDWjvg..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhFLQDUo2p5hPAKkdo597FH5JpX5KMhUgL.Fo-0eozEe0.4Soe2dJLoI0qLxK-LBo5L12qLxK-LBK-LBoeLxK-LBoMLB-zLxK-L12-L1hqLxK.L1K.LBK.LxKnLB--LBo5t; SUHB=0k1SR7G-ZVBoOQ; ALF=1505983605; SSOLoginState=1474447606; _s_tentry=login.sina.com.cn; UOR=www.baidu.com,vdisk.weibo.com,login.sina.com.cn; Apache=3959316008258.611.1474447606349; ULV=1474447606363:99:13:4:3959316008258.611.1474447606349:1474303861964"}
output=open('community.txt','a')
log_file='log_file.txt'
logging.basicConfig(filename = log_file, level = logging.DEBUG)
for page in range(1,1556):
	logging.info(page)
	url="http://service.account.weibo.com/index?type=5&status=4&page=%d"%page#爬取不实消息的页面
	logging.info(url)
	website = requests.get(url, cookies = cook) #等价于下面两句话
	if(website.ok):
		html=website.content
	elif(website.status_code == 404):
		logging.error("Failed(404): "+url )
		continue
	else:
		logging.error("time out: "+url )
		sys.exit(0)
	html=website.content# html = requests.get(url, cookies = cook).text   html = bytes(bytearray(html, encoding='utf-8'))
	mis_pattern=re.compile('<script>STK && STK\.pageletM && STK\.pageletM\.view\(\{"pid":"pl_service_showcomplaint",.*')
	misInformation=re.findall(mis_pattern,html)
	#print misInformation
	rid_pattern=re.compile('(rid=.*?)\\\\')
	rid=re.findall(rid_pattern,misInformation[0])
	for i in rid:
		output.write(i.encode('utf8')+'\n')
	#print rid
	page+=1
output.close()