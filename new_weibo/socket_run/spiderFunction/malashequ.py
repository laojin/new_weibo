from bs4 import BeautifulSoup
import json
import requests


def deal_index_page(response):
    datasoup=BeautifulSoup(response.text,'lxml')
    for i in datasoup.select('#threadlisttableid tbody')[1:]:
        try:
            print '------------------'
            print i.select('tr > th > a.s.xst')[0].text
        except Exception as e:
            print e




if __name__ == '__main__':
    url='http://www.mala.cn/forum-70-2.html'
    response=requests.get(url=url)
    deal_index_page(response)
