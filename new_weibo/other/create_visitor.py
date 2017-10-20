#_*_coding:utf-8_*_
import requests
import cookielib
import urllib
import json
import os
import time
import sys
import pickle
import pymongo
from bs4 import BeautifulSoup


mongoclient=pymongo.MongoClient('localhost',27017)
weiboCOL=mongoclient['weibo']
userDOC=weiboCOL['weibo_user']



data={
    'cb':'gen_callback',
    'fp':{"os":"2","browser":"Chrome61,0,3163,100","fonts":"undefined","screenInfo":"1920*1080*24","plugins":"Portable Document Format::internal-pdf-viewer::Chrome PDF Plugin|::mhjfbmdgcfjbbpaeojofohoefgiehjai::Chrome PDF Viewer|::internal-nacl-plugin::Native Client|Enables Widevine licenses for playback of HTML audio/video content. (version: 1.4.8.1008)::widevinecdmadapter.dll::Widevine Content Decryption Module"}
}


headers={
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'connection':'close',
    'cookie':''
}

class visitor_producer:

    def __init__(self):
        self.session=requests.session()
        self.cookies=cookielib.LWPCookieJar()
        self.headers={
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'connection':'close',
            'cookie':''
        }
        self.cert_file=os.path.dirname(os.path.abspath(os.path.dirname(__file__)))+'/sinacom.pem'

    def get_tid(self,proxy=None):
        try:
            session=requests.session()
            session.cert=False
            if proxy:
                response=session.request(method='post',url='https://passport.weibo.com/visitor/genvisitor',data=data,proxies=proxy,verify=False)
            else:
                response = session.request(method='post', url='https://passport.weibo.com/visitor/genvisitor', data=data,verify=False)
            response.close()
            session.close()
            print response.text
            data_raw=response.text.split('(')[1].rstrip(');')
            datajson=json.loads(data_raw)
            return {
                'tid':datajson['data']['tid'].replace('\\',''),#貌似可以不用处理tid中的\
                'proxy':proxy
            }
        except Exception as e:
            print e
            try:
                session.close()
            except Exception as e:
                print e
                pass
            return None

    def cookies_producer(self,tid):
        proxy=tid['proxy']
        tid=tid['tid']

        headers['Referer']='https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=http%3A%2F%2Fweibo.com%2F&domain=.weibo.com&ua=php-sso_sdk_client-0.6.23'
        headers['cookie']+='tid='+tid+'=__095'
        session1=requests.session()
        session1.cookies.set(name='tid',value=tid+'=__095')
        tid_url=urllib.urlencode({'t':tid})
        url_to_get_cookie='https://passport.weibo.com/visitor/visitor?a=incarnate&'+tid_url+'&w=2&c=095&gc=&cb=cross_domain&from=weibo'
        response=session1.request(method='get',url=url_to_get_cookie,params=None,data=None,headers=headers,verify=False)
        response.close()
        data_raw=response.text.split('(')[1].rstrip(');')
        datajson=json.loads(data_raw)

        cookiedict={
            'tid':str(tid)#设置到headers中的时候需要+'=__095'
        }

        a= response.cookies.iteritems()
        for i in a:
            key=i[0]
            value=i[1]
            one_cookie_dict={
                key:value
            }
            cookiedict.update(one_cookie_dict)

        finally_cookie={
            'cookiedict':cookiedict,
            'proxy':proxy
        }
        return finally_cookie

    def last_visit_last_response(self,cookiedict):

        proxy=cookiedict['proxy']
        cookiedict=cookiedict['cookiedict']
        #因为要是改变了self的headers，会对以后的访问造成影响，而且headers中的cookie是以字符串的形式发送过去的，所以将来cookie如果发生了改变，怎个cookie字段都要全部从新生成。
        headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'connection': 'close',
            'cookie': ''
        }
        sub = cookiedict['SUB']
        subp = cookiedict['SUBP']
        last_url='https://login.sina.com.cn/visitor/visitor?a=crossdomain&cb=return_back&s='+sub+'&sp='+subp+'&from=weibo'#这个url几乎没有什么用,返回的cookie也都是上一个链接里边有的.

        for one_cookie_dict in cookiedict.iteritems():
            self.session.cookies.set(one_cookie_dict[0],one_cookie_dict[1])

        headers_cookie_str=self.create_headers_cookies_str(cookiedict)
        headers['cookie']=headers_cookie_str
        response=self.session.request(method='get',url=last_url,headers=headers,verify=False)
        cookie_a=response.cookies.iteritems()
        for i in cookie_a:
            self.session.cookies.set(i[0],i[1])
            cookiedict.update(
                {
                    i[0]:i[1]
                }
            )
        response.close()

        #更新了session中的cookie，更新了字典中的cookie，以后
        if not proxy:
            proxy=int(time.time())
        result={
            'cookiedict':cookiedict,
            'proxy':proxy,
            'tid':cookiedict['tid']
        }
        try:
            userDOC.insert(result)
        except Exception as e:
            print e
        pass

    def create_headers_cookies_str(self,cookiedict):

        cookiestr=''
        for one_cookie_tuple in cookiedict.iteritems():
            if one_cookie_tuple[0]=='tid':#单独对tid独立做处理。
                one_cookie_str=one_cookie_tuple[0]+'='+one_cookie_tuple[1]+'=__095;'
            else:
                one_cookie_str=one_cookie_tuple[0]+'='+one_cookie_tuple[1]+';'
            cookiestr+=one_cookie_str

        return cookiestr




def initWeiboUserDB():
    userDOC.ensure_index('proxy',unique=True)



if __name__ == '__main__':
    thisclass=visitor_producer()

    initWeiboUserDB()

    tid_proxy=thisclass.get_tid()
    if tid_proxy:
        cookie_proxy=thisclass.cookies_producer(tid=tid_proxy)
        if cookie_proxy:
            thisclass.last_visit_last_response(cookiedict=cookie_proxy)