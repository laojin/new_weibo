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
    def __init__(self):
        self.host='127.0.0.1'
        self.taskqueue=Queue.Queue(maxsize=1000)

    def socket_recv(self,socket_port):
        socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket1.bind((self.host, socket_port))
        socket1.listen(5)
        print '已经进入监听线程里边了,正在监听端口: ',socket_port
        while True:
            conn,addr=socket1.accept()
            self.start_newthreading(conn=conn,addr=addr)

        socket1.close()


    def start_newthreading(self,conn,addr):
        data = conn.recv(1024)
        data=json.loads(data)
        _msg_type=data[MSG_TYPE]

        #选择执行一个函数
        if _msg_type=='get_task_url':
            threading.Thread(target=self.send_back_task,args=(conn,addr))
        elif _msg_type==REGISTER:
            threading.Thread(target=self.register,args=(conn,addr))



    def send_back_task(self,conn,addr):

        url=self.taskqueue.get()
        _dict1={
            'url':url
        }
        _datajson=json.dumps(_dict1)
        conn.sendall(_datajson)
        data=conn.recv(1024)
        print data
        conn.close()

    def register(self,conn,addr):
        data=conn.recv(1024)
        data=json.loads(data)
        print '收到来自',addr,'的注册请求,并接收到数据:',data
        conn.close()

    def heartbeat(self,conn,addr):
        data=conn.recv(1024)
        data=json.loads(data)
        print '收到来自',addr,'的心跳包,并接受到数据:',data

    def unregister(self,conn,addr):
        data=conn.recv(1024)
        data=json.loads(data)
        print '接受到来自',addr,'的取消注册消息,并接受到的数据是',data

    def dealunkonwnmsg(self,conn,addr,msg_type=None):
        # data=conn.recv(1024)
        # data=json.loads(data)
        print '接受到来自',addr,'的未知消息,消息类型是',msg_type










    def run(self,portlist=None):
        portlist = [20001, 20002, 20003, 20004]
        processlist = []
        for socket2 in portlist:
            process1 = process.Process(target=self.socket_recv, args=(socket2,))
            process1.start()
            processlist.append(process1)
        for process2 in processlist:
            process2.join()



# if __name__ == '__main__':
#     portlist=[20001,20002,20003,20004]
#     # socketlist=server(portlist=portlist)
#     # pool1=pool.Pool(processes=4)
#     # pool1.map(socket_recv,socketlist)
#     # pool1.close()
#     # pool1.join()
#     # socket1=socketlist.pop()
#     # process1=process.Process(target=socket_recv,args=(socket1,))
#     # process1.start()
#     processlist=[]
#     for socket2 in portlist:
#         process1=process.Process(target=socket_recv,args=(socket2,))
#         process1.start()
#         processlist.append(process1)
#     for process2 in processlist:
#         process2.join()
