#-*-coding:utf8-*-
#本程序主要用来爬取每个真实页面中的文本内容及用户信息
#输出格式为 #输出格式为 标签\t用户id\t微博id\t微博数\t关注数\t粉丝数\t昵称\t性别\t地点\t被举报微博内容\t发帖时间\t转发数\t评论数\t点赞数\n
#'comment'\t用户id\t微博数\t关注数\t粉丝数\t昵称\t性别\t地点\t评论内容
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
pattern = r"\d+\.?\d*"
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
		#任意抽取3页进行爬取
		select_list=range(2,number_of_pages+1)
		page_select=random.sample(select_list,min(number_of_pages/2,3))
		for number in page_select:
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
def get_fans(user_id):
	global crawled_account
	global cook
	global cook_index
	global number
	fans=[]
	url='http://weibo.cn/%s/fans'%user_id
	try:
		website=requests.get(url, cookies = cook)
		number+=1
		cook,cook_index=func(cook_list,cook_index,number)
		html=link_success(website,url)
		if html=='':
			return fans
		selector = etree.HTML(html)
		if selector.xpath('//input[@name="mp"]')==[]:
			pageNum = 1
		else:
			pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value'])
		for page in range(1,pageNum+1):#爬取所有页
			url='http://weibo.cn/%s/fans?page=%d'%(user_id,page)
			html = requests.get(url, cookies = cook).content
			selector = etree.HTML(html)
			info = selector.xpath("//div[@class='c']/table//a/@href")
			#检查该用户是否已经爬取过
			fans_i=[info[i].strip().split('/')[-1] for i in range(0,len(info),3) if info[i].strip().split('/')[-1] not in crawled_account]
			fans.extend(fans_i)
	except Exception,e:
		logging.info("error"+url)
	return fans

def get_follow(user_id):
	global crawled_account
	global cook
	global cook_index
	global number
	follow=[]
	url='http://weibo.cn/%s/follow'%user_id
	try:
		website=requests.get(url, cookies = cook)
		number+=1
		cook,cook_index=func(cook_list,cook_index,number)
		html=link_success(website,url)
		if html=='':
			return follow
		selector = etree.HTML(html)
		if selector.xpath('//input[@name="mp"]')==[]:
			pageNum = 1
		else:
			pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value'])
		for page in range(1,pageNum+1):#爬取所有页
			url='http://weibo.cn/%s/follow?page=%d'%(user_id,page)
			html = requests.get(url, cookies = cook).content
			selector = etree.HTML(html)
			info = selector.xpath("//table//a/@href")
			#检查该用户是否已经爬取过
			#follow_i=[info[i].strip().split('/')[-1] for i in range(0,len(info),3) if info[i].strip().split('/')[-1] not in crawled_account]利用这种方式时，获取到的用户id可能不是数字，比如lunaltt（1683579120），但是当我们爬取评论内容时最好是利用id
			follow_i=[info[i+2].split('uid=')[1].split('&')[0] for i in range(0,len(info),3) if info[i+2].split('uid=')[1].split('&')[0] not in crawled_account]
			follow.extend(follow_i)
	except Exception,e:
		logging.info("error"+url)
	return follow
		
def crawl_user(user_id):#爬取关于该用户的微博
	global crawled_account
	global cook
	global cook_index
	global number
	
	url='http://weibo.cn/%s?filter=1&page=1'%user_id
	try:
		website = requests.get(url, cookies = cook)
		number+=1
		cook,cook_index=func(cook_list,cook_index,number)
		html=link_success(website,url)
		if html=='':
			return 
		
		selector = etree.HTML(html)	
		if selector.xpath('//input[@name="mp"]')==[]:
			pageNum = 1
		else:
			pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value'])
		if pageNum < 3:#原创微博小于3页时，不进行爬取
			return
		user=getUserInfor(user_id)#返回用户的[微博数、关注数、粉丝数、昵称、性别、地区]
		#已经爬取过了加入set集合中
		crawled_account.add(user_id)
		#从原创微博中随机选取3页，爬取这3页的微博文本
		select_list=range(1,pageNum+1)
		page_select=random.sample(select_list,min(pageNum/2,3))
		
		for page in page_select:
			try:
				url='http://weibo.cn/%s?filter=1&page=%d'%(user_id,page)
				html = requests.get(url, cookies = cook).content
				selector = etree.HTML(html)	
				number+=1
				cook,cook_index=func(cook_list,cook_index,number)
				info = selector.xpath("//div[@class='c']")
				if len(info) > 3:
					for i in range(0,len(info)-2):
						try:
							forwarding = info[i].xpath("div/a/text()")[-3]
							guid = re.findall(pattern, forwarding, re.M)	
							num_forwarding = int(guid[0])#获取转发数
							if num_forwarding<20:
								continue
							comment_id=info[i].get('id').split('M_')[1]
							comment=getCommentInfor(user_id,comment_id)
							if len(comment) <4:#comment存转发评论点赞评论文本
								continue
							if len(comment[3])<2:
								continue
							
							#写到文件中
							#用户id,微博id
							output_truth.write('0'+'\t'+user_id+'\t'+comment_id)
							#用户信息，微博数\t关注数\t粉丝数\t昵称\t性别\t地点
							for i in user:
								output_truth.write('\t'+i.encode('utf-8'))
							#该微博内容
							output_truth.write('\t'+comment[3][1].encode('utf-8'))
							#转发数、评论数、点赞数
							for i in range(0,3):
								output_truth.write('\t'+comment[i].encode('utf-8'))
							output_truth.write('\n')
							#将评论写入文本
							for i in range(2,len(comment[3]),2):
								user=getUserInfor(comment[3][i])
								#time.sleep(10)
								output_truth.write('comment'+'\t'+comment[3][i].encode('utf-8'))
								for j in user:
									output_truth.write('\t'+j.encode('utf-8'))
								output_truth.write('\t'+comment[3][i+1].encode('utf-8')+'\n')
								output_truth.flush()
						except Exception,e:
							logging.info('error'+url)
			except Exception,e:
				logging.info('error'+url)
	except Exception,e:
		logging.info('error'+url)
#文件		
log_file='truth_logfile.txt'
logging.basicConfig(filename = log_file, level = logging.DEBUG)
#output_truth=open('truth.txt','a')

#设置cook
cook_list=getCookies()
cook_index=int(0)
cook=cook_list[cook_index]
number=int(0)
#设置初始账号
account=['2437229713']
account_cnt=int(0)
crawled_account=set()#已经爬取过的用户

while account_cnt<50000 and account_cnt<len(account):
	#爬取该用户的微博文本，并写入文件中
	if account_cnt%5000==0:
		output_truth=open('truth'+str(account_cnt/5000)+'.txt','a')
	crawl_user(account[account_cnt])
	#获取该用户的粉丝并爬取
	follow=get_follow(account[account_cnt])
	account.extend(follow)
	account_cnt+=1
output_truth.close()
crawled_file=open("crawled_account.txt",'w')
for user_id in crawled_account:
	crawled_file.write(user_id+'\n')
crawled_file.close()