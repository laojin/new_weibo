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





class server:
    urllist=['www.{}.com'.format(str(i)) for i in range(10)]
    def __init__(self):
        self.host='127.0.0.1'
        self.task_without_finish_queue=Queue.Queue(maxsize=1000)
        self.msg_need_to_send_to_master=Queue.Queue(maxsize=1000)
        for url in self.urllist:
            self.task_without_finish_queue.put(url)


    def socket_recv(self,socket_port):
        socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket1.bind((self.host, socket_port))
        socket1.listen(5)
        print '已经进入监听进程里边了,正在监听端口: ',socket_port
        while True:
            conn,addr=socket1.accept()
            self.start_newthreading(conn=conn,addr=addr)
            print socket_port,'端口收到了一个连接,'

        socket1.close()




    def start_newthreading(self,conn,addr):
        data = conn.recv(1024)
        data=json.loads(data)
        _msg_type=data[MSG_TYPE]

        #选择执行一个函数
        #可以用getattr函数来获得self中的相应的函数对象
        if _msg_type=='get_task_url':
            thread1=threading.Thread(target=self.send_back_task,args=(conn,addr))
        elif _msg_type==REGISTER:
            thread1 =threading.Thread(target=self.register,args=(conn,addr))
        elif _msg_type == HEARTBEAT:
            thread1 =threading.Thread(target=self.heartbeat,args=(conn,addr))
        elif _msg_type == UNREGISTER:
            thread1 =threading.Thread(target=self.unregister,args=(conn,addr))
        elif _msg_type == GET_VISITOR_INFO:
            thread1 =threading.Thread(target=server.getVisitorInfo,args=(conn,addr))
        else:
            thread1 =threading.Thread(target=self.dealunkonwnmsg,args=(conn,addr))
        thread1.start()
        # thread1.join()







    #########以下这部分主要负责和client端交互
    def send_back_task(self,conn,addr):

        url=self.task_without_finish_queue.get()
        _dict1={
            'url':url
        }
        _datajson=json.dumps(_dict1)
        conn.sendall(_datajson)
        data=conn.recv(1024)
        print data
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
        print '收到来自',addr,'的注册请求,并接收到数据:',data
        conn.close()
        dict2={
            MSG_TYPE:REGISTER,
        }
        data3={
            'data':data
        }

        try:
            _socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            _socket.connect(('127.0.0.1',40001))
            _dict2=json.dumps(dict2)
            self.sendmsg(jsonMSG=_dict2,sock=_socket)
            # print _dict2
            # _socket.sendall(_dict2)
            # _data2=_socket.recv(1024)
            # print _data2
            _data3=json.dumps(data3)
            # _data3=json.dumps(data3)
            # print _data3
            # _socket.sendall(_data3)
            self.sendmsg(jsonMSG=_data3,sock=_socket)
            _socket.close()
        except Exception as e:
            print e

    def heartbeat(self,conn,addr):
        # data=conn.recv(1024)
        data=self.recvmsg(conn=conn,addr=addr)
        print data
        data=json.loads(data)
        print '收到来自',addr,'的心跳包,并接受到数据:\n',data
        conn.close()

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
        processlist = []
        for socket2 in portlist:
            process1 = process.Process(target=self.socket_recv, args=(socket2,))
            process1.start()
            processlist.append(process1)
        for process2 in processlist:
            process2.join()



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