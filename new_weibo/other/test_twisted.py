import socket



sock1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# sock1.connect(('127.0.0.1',30001))

# sock1.sendall('hello')
# sock1.close()

sock1.bind(('127.0.0.1',30001))
sock1.listen(5)

while True:
    conn,addr=sock1.accept()
    data=conn.recv(1024)
    print data
    print addr,'\n'
    conn.close()