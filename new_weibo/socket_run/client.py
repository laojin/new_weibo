import socket


s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)


host='127.0.0.1'
# s.bind((host,57232))
s.connect((host,20004))
s.send('hello')
s.close()