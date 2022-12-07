import socket 
from common.connection import *

class Server:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.bind(('', 1234))
        self.sock.listen(5)

        while True:
            self.c, addr = self.sock.accept()
            print("Connected with the Client")
            break

        self.auth()
    
    def auth(self):
        self.conn = Connect(self.c)
        opt = self.conn.recvData()
        
        while True:
            out = False
            if opt == "login":
                out = self.conn.login()
            else:
                out = self.conn.register()
            
            if out:
                break
            else:
                self.conn.sendData("Auth Failed, Please retry")
    
    def __del__(self):
        self.c.close()