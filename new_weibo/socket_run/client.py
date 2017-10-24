#_*_coding:utf-8_*_
import socket
from protocol import *
import json
import time
import random

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
_first_msg={
    MSG_TYPE:REGISTER
}

time.sleep(2)
first_msg=json.dumps(_first_msg)
host='127.0.0.1'
# s.bind((host,57232))
s.connect((host,20001))
s.send(first_msg)
time.sleep(2)
_data=s.recv(1024)
print _data


spider_register={
    'spider_id':'127.0.0.1:'+str(random.randint(10000,50000)),
    'spider_start_time':time.time(),
    'spider_is_live':True,

}


secend_msg=json.dumps({'content':'这是我注册代码,5秒后连接将会断开.'})
s.send(secend_msg)
time.sleep(2)
s.close()