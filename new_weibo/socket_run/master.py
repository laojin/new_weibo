#_*_coding:utf-8_*_
import pymongo
import json
import socket
import threading
from multiprocessing import process
import Queue
from protocol import  *
import time
from bs4 import BeautifulSoup



class master:
    def __init__(self):
        self.pymongoclient=pymongo.MongoClient('localhost',27017,connect=False)
        self.weiboCOL=self.pymongoclient['weibo']
        self.weibo_userDOC=self.weiboCOL['weibo_user']
        self.weibo_dataDOC=self.weiboCOL['weibo_data']
        self.weibo_spider_clientDOC=self.weiboCOL['weibo_spider_clientDOC']
        self.weibo_task_url_list=self.weiboCOL['weibo_task_url']
        self.portlist=[40001,40002,40003,40004]

        self.task_url_list=[]
        self.task_url_finished_queue=Queue.Queue()
        self.spider_status_list=[]

    def establish_listen(self,port):
        socket1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        socket1.bind(('127.0.0.1',port))
        socket1.listen(5)
        while True:
            conn,addr=socket1.accept()
            self.start_newthreading(conn=conn,addr=addr)

    def start_newthreading(self,conn,addr):
        data=''
        data=self.recvmsg(conn=conn)
        data=json.loads(data)
        msg_type=data[MSG_TYPE]
        function1=getattr(self,msg_type)
        if function1:
            print function1
            thread1=threading.Thread(target=function1,args=(conn,addr))
            thread1.start()
            print '在function中'
        else:
            print '在else中'
            conn.close()


#以下的函数都是从server发送过来的，名称于serever上的这个函数方法名称一样
    def REGISTER(self,conn,addr):

        data=self.recvmsg(conn=conn,addr=addr)
        data=json.loads(data)
        self.weibo_spider_clientDOC.insert(data)
        conn.close()

    def UNREGISTER(self,conn,addr):
        # while True:
        #     while self.spider_status_list:
        #         msg=self.spider_status_list.pop()
        #         if msg[MSG_TYPE]==REGISTER:
        #             spider_info=msg['spider_info']
        #             self.weibo_spider_clientDOC.insert(spider_info)
        #         elif msg[MSG_TYPE]==UNREGISTER:
        #             spider_info=msg['spider_info']
        #             self.weibo_spider_clientDOC.delete_many({'ip':spider_info['ip']})
        #     time.sleep(1)
        data = self.recvmsg(conn=conn, addr=addr)
        data = json.loads(data)
        # self.weibo_spider_clientDOC.delete_many()#应该是update
        conn.close()

    def ADD_TASK_URL(self,conn,addr):#这个是server发送过来的要求添加task_url的请求，
        # _task_url_list=self.weibo_task_url_list.find().count(100)
        _task_url_list=['http://www.mala.cn/forum-70-{}.html'.format(str(i)) for i in range(500)]
        print '在add_task_url中'
        for i in _task_url_list:
            self.task_url_list.append(i)
        task_url_list_dict={
            'task_url_list':self.task_url_list
        }
        task_url_list_dict_json=json.dumps(task_url_list_dict)
        self.sendmsg(jsonMSG=task_url_list_dict_json,conn=conn,addr=addr)
        conn.close()

    def SEND_BACK_DATA(self,conn,addr):#这个也是从server端接收到的，不是发送给其它客户端的。
        data=self.recvmsg(conn=conn,addr=addr)
        data=json.loads(data)
        web_page_html=data['result']
        conn.close()

    def deal_html_func(self,html_page):
        datasoup=BeautifulSoup(html_page,'lxml')
        print datasoup.select('')



#与人交互函数

    def control_panel(self):
        while True:
            print '你现在在控制面板中,请输入你想执行的功能:1、显示所有正在运行的爬虫'
            imput1=raw_input()






    def run(self):
        # process1=process.Process(target=self.establish_listen,args=(40001,))#与server交互
        # process1.start()
        thread1 = threading.Thread(target=self.establish_listen, args=(40001,))
        thread1.start()


    def recvmsg(self,conn=None, sock=None, addr=None):
        s = conn if conn else sock
        s.settimeout(20)
        len_of_data = s.recv(1024)
        len_of_data = json.loads(len_of_data)
        data_finish = json.dumps({
            MSG_TYPE: STATUS_FINISH
        })
        s.sendall(data_finish)

        len_data = len_of_data['len_data']

        data = ''
        while True:
            _data = s.recv(1024)
            data += _data
            if len(data) >= len_data:
                break
        s.sendall(data_finish)

        return data

    def sendmsg(self,jsonMSG=None, conn=None, sock=None, addr=None):
        s = conn if conn else sock
        s.settimeout(20)
        len_of_data = len(jsonMSG)
        data_len_json = json.dumps({
            'len_data': len_of_data
        })
        # while True:#觉得这个while True，没有太大的意义
        s.sendall(data_len_json)
        data_resp = s.recv(1024)
        data_resp = json.loads(data_resp)
        if data_resp[MSG_TYPE] == STATUS_FINISH:
            pass

        while True:
            s.sendall(jsonMSG)
            data_resp = s.recv(1024)
            data_resp = json.loads(data_resp)
            if data_resp[MSG_TYPE] == STATUS_FINISH:
                break



if __name__ == '__main__':
    thisclass=master()
    thisclass.run()