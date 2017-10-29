#_*_coding:utf-8_*_
import socket
from protocol import *
import json
import time
import random
import requests
import datetime
import Queue
import threading


# s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# _first_msg={
#     MSG_TYPE:REGISTER
# }
#
# time.sleep(2)
# first_msg=json.dumps(_first_msg)
# host='127.0.0.1'
# # s.bind((host,57232))
# s.connect((host,20001))
# s.send(first_msg)
# time.sleep(2)
# _data=s.recv(1024)
# print _data



spider_register={
    'spider_id':'127.0.0.1:'+str(random.randint(10000,50000)),
    'spider_start_time':time.time(),
    'spider_is_live':True,

}
#
#
# secend_msg=json.dumps({'content':'这是我注册代码,5秒后连接将会断开.'})
# s.send(secend_msg)
# time.sleep(2)
# s.close()


class client:
    def __init__(self):
        self.session=requests.session()
        self.task_port=20001
        self.send_data_port=20002
        self.control_port=20004
        self.self_control_port=30001
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.remote_addr='192.168.6.105'
        self.client_id='mark123'

        self.task_queue=Queue.Queue(maxsize=10)


        self.REGISTER_MSG={
            MSG_TYPE:REGISTER
        }
        self.SEND_BACK_DATA_MSG={
            MSG_TYPE:SEND_BACK_DATA
        }
        self.UNREGISTER_MSG={
            MSG_TYPE:REGISTER
        }
        self.GET_TASK_URL_MSG={
            MSG_TYPE:GET_TASK_URL
        }

        self.HEARTBEAT_MSG={
            MSG_TYPE:HEARTBEAT,
            'spider_id':self.client_id
        }


        self.CONTROL_VARIABLE_LIVE=True


    def register(self):
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((self.remote_addr,self.control_port))
        self.sendmsg(jsonMSG=json.dumps(self.REGISTER_MSG),sock=sock)
        spider_register = {
            MSG_TYPE:REGISTER,
            'spider_id': '127.0.0.1:' + str(random.randint(10000, 50000)),
            'spider_start_time': time.time(),
            'spider_is_live': True,
        }
        self.sendmsg(jsonMSG=json.dumps(spider_register),sock=sock)
        sock.close()


    def get_task(self):
        while self.CONTROL_VARIABLE_LIVE:
            sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                sock.connect((self.remote_addr,self.task_port))
                self.sendmsg(jsonMSG=json.dumps(self.GET_TASK_URL_MSG),sock=sock)

                task_url_dict=self.recvmsg(sock=sock)
                task_url_dict=json.loads(task_url_dict)
                sock.close()
                while self.task_queue.full():
                    print '任务队列满了，等待2秒'
                    time.sleep(2)
                self.task_queue.put(task_url_dict)
            except Exception as e:
                print e
            finally:
                sock.close()


    def star_run_task(self):
        self.register()

        get_task_thread=threading.Thread(target=self.get_task,args=())
        heartbeat_thread=threading.Thread(target=self.HEARTBEAT,args=())
        listenserver_thread=threading.Thread(target=self.LISTEN_SERVER,args=())
        heartbeat_thread.start()
        listenserver_thread.start()
        get_task_thread.start()



        while self.CONTROL_VARIABLE_LIVE:
            while not self.task_queue.empty():
                #以后直接将队列传入，这样是否需要多线程，都可以在函数中定义。
                task_dict=self.task_queue.get()
                task_url=task_dict['task_url']
                response=self.session.get(task_url)
                response_text=response.text
                #以上都在函数中处理


                result=self.deal_response(response_text)

                # yield result
                # self.send_back_data(result)
                # print len(result)
                try:
                    self.send_back_data(result=result,url=task_url)
                except Exception as e:
                    print e
                print

            print '当前爬虫客户端的任务队列已经执行完毕，5秒后将会再次检测队列任务。'
            time.sleep(5)

        self.UNREGISTER()
        print '客户端即将在5秒后结束'
        time.sleep(5)


    def UNREGISTER(self):
        self.socket.connect((self.remote_addr,self.control_port))
        self.sendmsg(jsonMSG=json.dumps(self.UNREGISTER_MSG),sock=self.socket)
        self.socket.close()


    def send_back_data(self,result,url,need_send_to_master=False):
        result_dict={
            'result':result,
            'client_id':self.client_id,
            'produce_time':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'url':url,
            MSG_TYPE:None,
            NEED_TO_SEND_MASTER:need_send_to_master
        }
        socket1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        socket1.connect((self.remote_addr,self.send_data_port))
        self.sendmsg(jsonMSG=json.dumps(self.SEND_BACK_DATA_MSG),sock=socket1)
        self.sendmsg(jsonMSG=json.dumps(result_dict),sock=socket1)
        socket1.close()


    def deal_response(self,response_text):
        print '数据已经处理过了'

        return response_text


    def HEARTBEAT(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.remote_addr, self.control_port))
        self.sendmsg(jsonMSG=json.dumps(self.HEARTBEAT_MSG), sock=sock)
        while self.CONTROL_VARIABLE_LIVE:
            try:
                self.sendmsg(jsonMSG=json.dumps(self.HEARTBEAT_MSG),sock=sock)
                time.sleep(2)
            except Exception as e:
                print e
                break
        sock.close()


    def LISTEN_SERVER(self):
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.bind(('127.0.0.1',self.self_control_port))
        sock.listen(5)
        while True:
            conn,addr=sock.accept()
            data=self.recvmsg(conn=conn,addr=addr)
            data=json.loads(data)
            conn.close()
            if data[MSG_TYPE]==CLIENT_STOP:
                self.CONTROL_VARIABLE_LIVE=False
                break
        sock.close()


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


if __name__ == '__main__':
    clientclass=client()
    clientclass.star_run_task()