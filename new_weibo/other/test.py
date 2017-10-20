#_*_coding:utf-8_*_
import requests
import pymongo
import json
from bs4 import BeautifulSoup




mongoclient=pymongo.MongoClient('localhost',27017)
weiboCOL=mongoclient['weibo']
userDOC=weiboCOL['weibo_user']



def create_headers_cookies_str(cookiedict):
    cookiestr=''
    for one_cookie_tuple in cookiedict.iteritems():
        if one_cookie_tuple[0]=='tid':#单独对tid独立做处理。
            one_cookie_str=one_cookie_tuple[0]+'='+one_cookie_tuple[1]+'=__095;'
        else:
            one_cookie_str=one_cookie_tuple[0]+'='+one_cookie_tuple[1]+';'
        cookiestr+=one_cookie_str
    return cookiestr




persion_info=userDOC.find_one()
persion_dict=persion_info['cookiedict']
session1=requests.session()

for i in persion_dict.iteritems():
    session1.cookies.set(i[0],i[1])

headers_cookie_str=create_headers_cookies_str(persion_dict)

headers={
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'connection':'close',
    'cookie':''
}

headers['cookie']=headers_cookie_str

url='http://weibo.com/2549228714/Fr7GzFI4T?ref=feedsdk&type=comment#_rnd1508479298791'

response1=session1.request(method='get',url=url,headers=headers,proxies=None)
print response1.text
response1.close()
session1.close()