#-*-coding:utf8-*-
#本程序主要用来爬取每个谣言页面中的文本内容及用户信息
import requests
import re
from lxml import etree
from bs4 import BeautifulSoup as bs
import logging
import sys
import time
import httplib
from my_cookies import getCookies
import random
def func(cook_list,cook_index,number):
	if number%20==0:
		cook_index+=1
		if cook_index==len(cook_list):
			cook_index=0
		return cook_list[cook_index],cook_index
	return cook_list[cook_index],cook_index
def link_success(website,url):
	retry=3
	global cook
	global cook_index
	global number
	while retry>=0:
		if(website.ok):
			html=website.content
			return html
		elif(website.status_code == 404):
			logging.error("Failed(404): "+url )
			return ''
		elif (website.status_code == 403):
			time.sleep(10)
			requests.get('http://www.baidu.com/s?psid=sdafwewer'+str(1))
			website=requests.get(url, cookies = cook)
			number+=1
			cook,cook_index=func(cook_list,cook_index,number)
			retry-=1
		else:
			logging.error("time out: "+url )
			website=requests.get(url, cookies = cook)
			number+=1
			cook,cook_index=func(cook_list,cook_index,number)
			retry-=1
	return ''

def getReview(user_id,comment_id):
	global cook
	global cook_index
	global number
	comment_content=[]
	url='http://weibo.cn/comment/%s?uid=%s&rl=0#cmtfrm'%(comment_id,user_id)
	try:
		weibo_html=requests.get(url, cookies = cook).content
		number+=1
		cook,cook_index=func(cook_list,cook_index,number)
		# 爬取第一页的评论，评论都是在class为c的div里面
		comment = bs(weibo_html, 'lxml').find_all('div', class_="c")
		#print comment
		for i in range(len(comment)):
			if (comment[i].a is None) or (comment[i].span is None):
				continue
			#comment[i].a.text 获取用户的昵称
			#print comment[i].a.get('href').strip('/u/').encode('utf-8','ignore')
			#print comment[i].span.text.encode('utf-8','ignore')
			if comment[i].span.text.encode('utf-8')=='[热门]':
				continue
			comment_content.append(comment[i].a.get('href').lstrip('/'))#评论用户的id
			comment_content.append(comment[i].span.text)#评论文本

		pages = bs(weibo_html, 'lxml').find_all('div', class_="pa")
		try:
			# 这个是为了获得评论的页数，pages里面是一个字符串，所以就处理了一下
			number_of_pages = pages[0].div.text.split('/')[1][:-1]
		except IndexError:
			# 出现这个错误说明只有一页评论
			number_of_pages = 1
		for number in range(2, min(int(number_of_pages),3)):
			# 修改这个url的时候需要注意将url后面的#cmtfrm删掉
			weibo_url = url.strip('#cmtfrm') + "&page=%s" % number
			#print weibo_url
			time.sleep(10)
			rand_int = random.randint(1,999999)
			requests.get('http://www.baidu.com/s?psid=sdafwewer'+str(rand_int))
			weibo_html= requests.get(weibo_url, cookies=cook).text
			number+=1
			cook,cook_index=func(cook_list,cook_index,number)
			# 评论都是在class为c的div里面
			comment = bs(weibo_html, 'lxml').find_all('div', class_="c")
			# comment里面的前两个应该是发布者的信息，最后一个是HTML页面的一个信息，都不是用户的评论，所以去掉了
			for i in range(2, len(comment) - 1):
				if (comment[i].a is None) or (comment[i].span is None):
					continue
				if comment[i].span.text.encode('utf-8')=='[热门]':
					continue
				comment_content.append(comment[i].a.get('href').lstrip('/'))#评论用户的ID  这里得到的id格式为/choucou 或/u/5977108898
				comment_content.append(comment[i].span.text)#评论文本
	except Exception,e:
		logging.info("error"+start_url)
	'''
	except (requests.ConnectionError):
		logging.info("connection error"+url)
	except (httplib.IncompleteRead):
		logging.infor("httplib.IncompleteRead"+start_url)
	'''
	return comment_content

def getCommentInfor(user_id,comment_id):
	global cook
	global cook_index
	global number
	comment=[]#发帖对应的转发 评论 点赞
	url='http://weibo.cn/%s/%s?type=comment'%(user_id,comment_id)
	try:
		website=requests.get(url, cookies = cook)
		number+=1
		cook,cook_index=func(cook_list,cook_index,number)
		html=link_success(website,url)
		if html=='':
			return comment
		selector = etree.HTML(html)
		#content = selector.xpath('//*[@id="M_"]/div/span[2]')#发帖时间
		#print content[0].xpath('string(.)')
		#comment.append(content[0].xpath('string(.)'))
		pstr='/html/body/div[8]'
		content = selector.xpath(pstr+'/span[1]/a')#转发  已奔溃，在的位置还不一样，有的在div[7] 有的在div[8] /html/body/div[7]/span[1]/a /html/body/div[7]/span[3]/a
		if len(content)==0:
			pstr=pstr.replace('8','7')
			content = selector.xpath(pstr+'/span[1]/a')
		if len(content)==0:
			return comment
		comment.append(content[0].xpath('string(.)'))
		content = selector.xpath(pstr+'/span[2]')#评论
		comment.append(content[0].xpath('string(.)'))
		content = selector.xpath(pstr+'/span[3]/a')#点赞
		comment.append(content[0].xpath('string(.)'))
		comment_content=getReview(user_id,comment_id)#评论文本，用户id 评论内容 用户id 评论内容 .... 第一个为当前用户，当前微博内容
		comment.append(comment_content)
	except Exception,e:
		logging.info("error"+start_url)
	'''
	except (requests.ConnectionError):
		logging.info("connection error"+url)
	except (httplib.IncompleteRead):
		logging.infor("httplib.IncompleteRead"+start_url)
	'''
	return comment

def getUserInfor(user_id):
	global cook
	global cook_index
	global number	
	user=[]
	url='http://weibo.cn/%s'%user_id#http://weibo.cn/cyld664170 利用这个链接可以访问到用户微博数、关注数、粉丝数，但是要爬取资料还是需要他的确切id http://weibo.cn/3144213803/info
	try:
		website=requests.get(url, cookies = cook)
		number+=1
		cook,cook_index=func(cook_list,cook_index,number)
		html=link_success(website,url)
		if html=='':
			return user
		selector = etree.HTML(html)
		content = selector.xpath('/html/body/div[3]/div/span')#微博数 /html/body/div[3]/div/span
		if len(content)==0:
			return user
		user.append(content[0].xpath('string(.)'))
		content = selector.xpath('/html/body/div[3]/div/a[1]')#关注数 /html/body/div[3]/div/a[1]
		user.append(content[0].xpath('string(.)'))
		content = selector.xpath('/html/body/div[3]/div/a[2]')#粉丝数 /html/body/div[3]/div/a[2]
		user.append(content[0].xpath('string(.)'))
		c=bs(html, 'lxml').find_all('div', class_="tip2")
		url='http://weibo.cn/%s/info'%c[0].a.get('href').strip('/follow')
		#time.sleep(10)
		website=requests.get(url, cookies = cook)
		number+=1
		cook,cook_index=func(cook_list,cook_index,number)
		html=link_success(website,url)
		user.extend(['']*3)
		if html=='':
			return user
		selector = etree.HTML(html)
		if len(selector.xpath('/html/body/div[6]/text()[1]'))!=0:
			user[3]= selector.xpath('/html/body/div[6]/text()[1]')[0]#昵称  .split(':')[1]
		if len(selector.xpath('/html/body/div[6]/text()[2]'))!=0:
			user[4]= selector.xpath('/html/body/div[6]/text()[2]')[0] #性别
		if len(selector.xpath('/html/body/div[6]/text()[3]'))!=0:
			user[5]= selector.xpath('/html/body/div[6]/text()[3]')[0]#地区
	except Exception,e:
		logging.info("error"+start_url)
	'''
	except (requests.ConnectionError):
		logging.info("connection error"+url)
	except (httplib.IncompleteRead):
		logging.infor("httplib.IncompleteRead"+start_url)
	'''
	return user
log_file='log_file2.txt'
logging.basicConfig(filename = log_file, level = logging.DEBUG)
cook_list=getCookies()
output_rumor=open('rumor_rid9.txt','a')#输出格式为 #输出格式为 标签\t用户id\t微博id\t微博数\t关注数\t粉丝数\t昵称\t性别\t地点\t被举报微博内容\t发帖时间\t转发数\t评论数\t点赞数\n
#'comment'\t用户id\t微博数\t关注数\t粉丝数\t昵称\t性别\t地点\t评论内容
rid=open('rid_9.txt').readlines()
cook_index=0
cook=cook_list[cook_index]
number=int(0)
for i in range(2917,len(rid)):#针对每条不实消息，进行爬取
	start_url="http://service.account.weibo.com/show?%s"%rid[i]
	logging.info(" crawl url "+start_url)
	try:
		website=requests.get(start_url, cookies = cook)
		number+=1
		cook,cook_index=func(cook_list,cook_index,number)	
		html=link_success(website,start_url)
		if html=='': #爬取此处遇到404
			continue
		mis_pattern=re.compile('<script>STK && STK\.pageletM && STK\.pageletM.view\(\{"pid":"pl_service_common.*')
		misInformation=re.findall(mis_pattern,html)
		if len(misInformation)==0:
			continue
		user_pattern=re.compile("value=original_text\\\\\" target='_blank' href=(.*?)\\\\u539f\\\\u6587")
		user=re.findall(user_pattern,misInformation[0])#查找原文按钮
		if len(user)==0:
			continue
		user_infor=user[0].lstrip("'http:\\/\\/weibo.com\\/").rstrip("'>\"").split('\\/')#用户的id及该微博的id
		logging.info(" user "+user_infor[0])
		logging.info(" weibo "+user_infor[1])
		#time.sleep(10)
		user=getUserInfor(user_infor[0])#爬取用户信息
		if len(user)==0:
			continue
		#time.sleep(10)
		comment=getCommentInfor(user_infor[0],user_infor[1])
		if len(comment) <4:
			continue
		if len(comment[3])<2:
			continue
		#用户id,微博id
		output_rumor.write('1'+'\t'+user_infor[0]+'\t'+user_infor[1])
		#用户信息，微博数\t关注数\t粉丝数\t昵称\t性别\t地点
		for i in user:
			output_rumor.write('\t'+i.encode('utf-8'))
		output_rumor.write('\t'+comment[3][1].encode('utf-8'))#该微博内容
		for i in range(0,3):
			output_rumor.write('\t'+comment[i].encode('utf-8'))#转发数、评论数、点赞数
		output_rumor.write('\n')
		for i in range(2,len(comment[3]),2):
			user=getUserInfor(comment[3][i])
			#time.sleep(10)
			output_rumor.write('comment'+'\t'+comment[3][i].encode('utf-8'))
			for j in user:
				output_rumor.write('\t'+j.encode('utf-8'))
			output_rumor.write('\t'+comment[3][i+1].encode('utf-8')+'\n')
	except Exception,e:
		logging.info("error"+start_url)
	#except (requests.ConnectionError):
	#	logging.info("connection error"+start_url)
	#except (httplib.IncompleteRead):
	#	logging.infor("httplib.IncompleteRead"+start_url)
output_rumor.close()