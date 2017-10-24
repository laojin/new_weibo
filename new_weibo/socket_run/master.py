#_*_coding:utf-8_*_
import pymongo
import json
import socket
import threading
from multiprocessing import process
import Queue
from protocol import  *
import time



class master:
    def __init__(self):
        self.pymongoclient=pymongo.MongoClient('localhost',27017,connect=False)
        self.weiboCOL=self.pymongoclient['weibo']
        self.weibo_userDOC=self.weiboCOL['weibo_user']
        self.weibo_dataDOC=self.weiboCOL['weibo_data']
        self.weibo_spider_clientDOC=self.weiboCOL['weibo_spider_clientDOC']
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

    def run(self):
        process1=process.Process(target=self.establish_listen,args=(40001,))
        process1.start()

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