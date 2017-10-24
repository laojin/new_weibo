#_*_coding:utf-8_*_
from protocol import *
import socket
import json

data=''
with open('test_socket','r') as fl:
    data= fl.read()


socket1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# socket1.bind(('127.0.0.1',45645))
# socket1.listen(5)




socket1.connect(('127.0.0.1',20001))

datasjon1={
    MSG_TYPE:REGISTER
}
_data1=json.dumps(datasjon1)
socket1.sendall(_data1)
#
datajson2={
    'data':data
}

_data2=json.dumps(datajson2)
# # socket1.sendall(_data2)
#
# print len(_data2)


# conn,addr=socket1.accept()

socket1.settimeout(5)

text='12312312313231312132132132133'


def sendmsg(jsonMSG=None,conn=None,sock=None,addr=None):
    s = conn if conn else sock
    s.settimeout(20)
    len_of_data = len(jsonMSG)
    data_len_json = json.dumps({
        'len_data': len_of_data
    })
    # while True:#觉得这个while True，没有太大的意义
    s.sendall(data_len_json)
    data_resp=s.recv(1024)
    data_resp=json.loads(data_resp)
    if data_resp[MSG_TYPE]==STATUS_FINISH:
        pass

    while True:
        s.sendall(jsonMSG)
        data_resp=s.recv(1024)
        data_resp=json.loads(data_resp)
        if data_resp[MSG_TYPE]==STATUS_FINISH:
            break
    s.close()



def recvmsg(conn=None,sock=None,addr=None):
    s=conn if conn else sock
    s.settimeout(20)
    len_of_data=s.recv(1024)
    len_of_data=json.loads(len_of_data)
    data_finish=json.dumps({
        MSG_TYPE:STATUS_FINISH
    })
    s.sendall(data_finish)

    len_data=len_of_data['len_data']

    data=''
    while True:
        _data=s.recv(1024)
        data+=_data
        if len(data)>=len_data:
            break
    s.sendall(data_finish)
    s.close()
    return data


sendmsg(jsonMSG=_data2,sock=socket1)