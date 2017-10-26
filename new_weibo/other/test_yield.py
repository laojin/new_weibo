import socket
import threading
from multiprocessing import process
import time




class client:
    def __init__(self):
        self.variable=True
        self.socket1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.test_url_list=['www.{}.com'.format(str(i)) for i in range(100)]


    def run(self):
        self.socket1.bind(('127.0.0.1',30002))
        while True:
            conn,addr=self.socket1.accept()
            data=conn.recv(1024)
            print data
            conn.close()


    def send_data(self,data):
        try:
            socket1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            socket1.connect(('127.0.0.1',30001))
        except Exception as e:
            print e
        # self.socket1.connect_ex()
        socket1.sendall(data)
        socket1.close()


    def start_send_msg(self):
        for ii in self.test_url_list:
            time.sleep(3)
            self.send_data(ii)

    def start_thread(self):
        thread1=threading.Thread(target=self.start_send_msg,args=())
        thread1.start()


if __name__ == '__main__':
    # thisclass=client()
    # thisclass.start_thread()
    socket1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket1.connect(("127.0.0.1",30001))
    socket1.sendall('hello--aaa')
    # socket1.close()
    # socket1.connect(('127.0.0.1',30001))
    socket1.sendall('hello---bbb')

