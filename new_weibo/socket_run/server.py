#_*_coding:utf-8_*_
import socket
import time
import threading
from multiprocessing.process import Process
from multiprocessing import process
from multiprocessing import pool
from protocol import *
import Queue
import json
import random





class server:
    # urllist=['http://www.mala.cn/forum-70-{}.html'.format(str(i)) for i in range(500)]
    def __init__(self):
        self.host='192.168.6.105'
        self.master_ip='127.0.0.1'
        self.master_data_port=40001

        self.SEND_BACK_DATA_MSG = {
            MSG_TYPE: SEND_BACK_DATA
        }
        self.ADD_TASK_URL_MSG={
            MSG_TYPE:ADD_TASK_URL
        }




        self.task_without_finish_queue=Queue.Queue(maxsize=1000)
        self.msg_need_to_send_to_master=Queue.Queue(maxsize=1000)
        # for url in self.urllist:
        #     self.task_without_finish_queue.put(url)


    def socket_recv(self,socket_port):
        socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket1.bind((self.host, socket_port))
        socket1.listen(20)
        print '已经进入监听进程里边了,正在监听端口: ',socket_port
        while True:
            conn,addr=socket1.accept()
            self.start_newthreading(conn=conn,addr=addr)
            print socket_port,'端口收到了一个连接,'

        socket1.close()


    def start_newthreading(self,conn,addr):
        data = self.recvmsg(conn=conn,addr=addr)
        data=json.loads(data)
        _msg_type=data[MSG_TYPE]

        #选择执行一个函数
        #可以用getattr函数来获得self中的相应的函数对象
        if _msg_type==GET_TASK_URL:
            thread1=threading.Thread(target=self.send_back_task,args=(conn,addr))
        elif _msg_type==REGISTER:
            thread1 =threading.Thread(target=self.register,args=(conn,addr))
        elif _msg_type == HEARTBEAT:
            thread1 =threading.Thread(target=self.heartbeat,args=(conn,addr))
        elif _msg_type == UNREGISTER:
            thread1 =threading.Thread(target=self.unregister,args=(conn,addr))
        elif _msg_type == GET_VISITOR_INFO:
            thread1 =threading.Thread(target=server.getVisitorInfo,args=(conn,addr))
        elif _msg_type==ADD_TASK_URL:
            thread1=threading.Thread(target=self)
        elif _msg_type==SEND_BACK_DATA:
            thread1=threading.Thread(target=self.SEND_BACK_DATA,args=(conn,addr))
        else:
            thread1 =threading.Thread(target=self.dealunkonwnmsg,args=(conn,addr))
        thread1.start()
        # thread1.join()


    #########以下这部分主要负责和client端交互
    def send_back_task(self,conn,addr):
        if self.task_without_finish_queue.empty():
            sock_get_task_from_master=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock_get_task_from_master.connect((self.master_ip,self.master_data_port))
            self.sendmsg(jsonMSG=json.dumps(self.ADD_TASK_URL_MSG),sock=sock_get_task_from_master)
            data=self.recvmsg(sock=sock_get_task_from_master)
            sock_get_task_from_master.close()
            data=json.loads(data)
            for task_url in data['task_url_list']:
                self.task_without_finish_queue.put(task_url)

        url=self.task_without_finish_queue.get()
        _dict1={
            'task_url':url
        }
        _datajson=json.dumps(_dict1)
        self.sendmsg(jsonMSG=_datajson,conn=conn)
        conn.close()

    def register(self,conn,addr):
        # _reply_data = {
        #     MSG_TYPE: MSG_RECV_OK
        # }
        # reply_data = json.dumps(_reply_data)
        # conn.sendall(reply_data)
        #
        # data=conn.recv(1024)
        data=self.recvmsg(conn=conn,addr=addr)
        data=json.loads(data)
        print '收到来自',addr,'的注册请求,并接收到数据:',data,'试图发送给master'

        conn.close()
        dict2={
            MSG_TYPE:REGISTER,
        }
        data['client_ip']=addr
        data3={
            'data':data
        }

        try:
            _socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            _socket.connect(('127.0.0.1',40001))
            _dict2=json.dumps(dict2)
            self.sendmsg(jsonMSG=_dict2,sock=_socket)
            _data3=json.dumps(data3)
            self.sendmsg(jsonMSG=_data3,sock=_socket)
            _socket.close()
            print '成功发送给了master'
        except Exception as e:
            print e
            print '注册到master失败了'

    def heartbeat(self,conn,addr):
        while True:
            try:
                data=self.recvmsg(conn=conn,addr=addr)
                print data
                data=json.loads(data)
                print '收到来自',addr,'的心跳包,说明爬虫',data['spider_id'],'还是活着的'
            except Exception as e:
                print e,'没有收到来自',addr,'的心跳包,说明爬虫',data['spider_id'],'死了'
                conn.close()
                break

    def unregister(self,conn,addr):
        data=conn.recv(1024)
        data=json.loads(data)
        print '接受到来自',addr,'的取消注册消息,并接受到的数据是',data

        conn.close()

    def dealunkonwnmsg(self,conn,addr,msg_type=None):
        # data=conn.recv(1024)
        # data=json.loads(data)
        print '接受到来自',addr,'的未知消息,消息类型是',msg_type
        conn.close()

    def getVisitorInfo(self,conn,addr):
        print '收到来自',addr,'的一个为了获取用户信息的连接'
        conn.close

    def SEND_BACK_DATA(self,conn,addr):
        _data=self.recvmsg(conn=conn,addr=addr)
        datajson=json.loads(_data)
        timestr=str(int(time.time()))+str(random.randint(1,200))
        try:
            with open('F:/project/testFBS/mala/html_file/'+timestr,'w+') as fl:
                json.dump(datajson,fl)
        except Exception as e:
            print e
        conn.close()
        if datajson[NEED_TO_SEND_MASTER]:#与后边的与master交互函数配合，往master中推送消息。
            sock_to_master=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock_to_master.connect((self.master_ip,self.master_data_port))
            self.sendmsg(jsonMSG=json.dumps(self.SEND_BACK_DATA_MSG))#发送给服务器的
            self.sendmsg(jsonMSG=json.dumps(datajson),sock=sock_to_master)
            sock_to_master.close()

    def SEND_CONTROL_CLIENT(self,conn=None,sock=None,addr=None,data_CONTROL=None):
        pass

    # def ADD_TASK_URL

    ##########以下这部分主要用于和master交互

    def socket_recv_master(self,socket_port=22222):
        socket1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            socket1.bind((self.host,socket_port))
            socket1.listen(5)
            while True:
                print '和master交互的socket已经开始监听端口:',socket_port,'正在等待连接.'
                conn,addr=socket1.accept()
                self.start_listen_master(conn=conn,addr=addr)
        except Exception as e:
            print e

    def add_task_url(self,conn,addr):
        data=conn.recv(1024)
        data=json.loads(data)
        for url in data['task_url_list']:
            self.task_without_finish_queue.put(url)
        conn.close()

    def send_msg_to_master(self):
        #---------------------!
        '''
        这里需要一个队列，因为每一次收到一个客户端的消息，就于master建立一次连接，将来并发太高，会导致同时连接数太多。
        :return:
        '''
        socket3=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        socket3.bind((self.host,))
        # socket3.sendall(msg)
        socket3.close()

    def recvmsg(self, conn=None, sock=None, addr=None):
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

    def sendmsg(self, jsonMSG=None, conn=None, sock=None, addr=None):
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






    def run(self,portlist=None):
        portlist = [20001, 20002, 20003, 20004]
        # processlist = []
        # for socket2 in portlist:
        #     process1 = process.Process(target=self.socket_recv, args=(socket2,))
        #     process1.start()
        #     processlist.append(process1)
        # for process2 in processlist:
        #     process2.join()

        threadlist = []
        for socket2 in portlist:
            thread1 = threading.Thread(target=self.socket_recv, args=(socket2,))
            thread1.start()
            threadlist.append(thread1)
        for thread2 in threadlist:
            thread2.join()



if __name__ == '__main__':
    # portlist=[20001,20002,20003,20004]
    # # socketlist=server(portlist=portlist)
    # # pool1=pool.Pool(processes=4)
    # # pool1.map(socket_recv,socketlist)
    # # pool1.close()
    # # pool1.join()
    # # socket1=socketlist.pop()
    # # process1=process.Process(target=socket_recv,args=(socket1,))
    # # process1.start()
    # processlist=[]
    # for socket2 in portlist:
    #     process1=process.Process(target=socket_recv,args=(socket2,))
    #     process1.start()
    #     processlist.append(process1)
    # for process2 in processlist:
    #     process2.join()

    thisclass=server()
    thisclass.run()