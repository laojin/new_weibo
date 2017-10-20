#_*_coding:utf-8_*_
import requests
import pymongo
import random

mongoclient=pymongo.MongoClient('localhost',27017)
weiboCOL=mongoclient['weibo']
weiboDOC=weiboCOL['weibo_user']


def create_headers_cookies_str(cookiedict):
    cookiestr=''
    for one_cookie_tuple in cookiedict.iteritems():
        if one_cookie_tuple[0]=='tid':#单独对tid独立做处理。
            one_cookie_str=one_cookie_tuple[0]+'='+one_cookie_tuple[1]+'=__095;'
        else:
            one_cookie_str=one_cookie_tuple[0]+'='+one_cookie_tuple[1]+';'
        cookiestr+=one_cookie_str
    return cookiestr

def get_persion_info(israndom=True):
    if israndom:
        persion_info_all=weiboDOC.find()
        persion_info_list=[]
        for persion_info in persion_info_all:
            persion_info_list.append(persion_info)
        persion_info_one=random.choice(persion_info_list)
    else:
        persion_info_one=weiboDOC.find_one()
    print persion_info_list
    return persion_info_one






class visitor:
    def __init__(self):
        self.session=requests.session()
        self.headers={
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'connection':'close',
    'cookie':''
}
        self.cookiedict={}

        self.mongoclient = pymongo.MongoClient('localhost', 27017)
        self.weiboCOL = mongoclient['weibo']
        self.weiboDOC = weiboCOL['weibo_user']
        self.proxy=None




    def get_persion_info(self,israndom=True):
        if israndom:
            persion_info_all = self.weiboDOC.find()
            persion_info_list = []
            for persion_info in persion_info_all:
                persion_info_list.append(persion_info)
            persion_info_one = random.choice(persion_info_list)
        else:
            persion_info_one = self.weiboDOC.find_one()
        return persion_info_one

    def init_self(self):
        self.persion_info = get_persion_info()
        self.proxy=self.persion_info['proxy']
        self.cookiedict=self.persion_info['cookiedict']
        for i in self.cookiedict.iteritems():
            self.session.cookies.set(i[0],i[1])
        self._id=self.persion_info['_id']



    def visit(self,url,headers=None,proxy=None,encoding='utf-8'):

        if not proxy:
            if '.' in str(self.proxy):
                proxy=self.proxy
        for i in self.cookiedict.iteritems():
            self.session.cookies.set(i[0],i[1])

        if not headers:
            headers=self.headers

        headers['cookie']=create_headers_cookies_str(self.cookiedict)
        response=self.session.request(method='get',url=url,headers=headers,proxies=proxy)
        for cookie_one_response in response.cookies.iteritems():
            self.cookiedict.update(
                {
                cookie_one_response[0]:cookie_one_response[1]
            }
            )
            self.session.cookies.set(cookie_one_response[0],cookie_one_response[1])
        response.close()
        response.encoding=encoding
        return response.text

    def __del__(self):
        for i in self.session.cookies.iteritems():
            self.cookiedict.update(
                {
                    i[0]:i[1]
                }
            )

        if 'tid' in self.cookiedict.keys():
            weiboDOC.update({'tid':self.cookiedict['tid']},{'$set':{'cookiedict':self.cookiedict}},upsert=True)

        self.session.close()



if __name__ == '__main__':
    thisclass=visitor()
    thisclass.init_self()
    print thisclass.visit(url='http://weibo.com/3623353053/FreU4A4EH?ref=feedsdk&type=comment#_rnd1508486724760')
    print thisclass.visit(url='http://weibo.com/3196649034/Fr8YjiXju?from=embedded_weibo&type=comment#_rnd1508489887783')
    del thisclass