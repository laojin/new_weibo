import socket
import time
from multiprocessing import Process
from multiprocessing import Pool


host='127.0.0.1'




def server(portlist=[]):
    socketlist=[]
    for i in portlist:
        socket1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        socket1.bind((host,i))
        socketlist.append(socket1)
        socket1.listen(5)
    for socket2 in socketlist:
        conn,addr=socket2.accept()
        conn.recv(1204)
        conn.close()
        socket2.close()


if __name__ == '__main__':
    portlist=[20001,20002,20003,20004]
    server(portlist=portlist)