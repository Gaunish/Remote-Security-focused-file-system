import socket 
from connection import *
from connect import *

class Server:
    def __init__(self):
        print("Waiting for a connection...")
        self.sock = socket.socket()
        self.sock.bind(('', 3002))
        self.sock.listen(5)

        while True:
            self.c, addr = self.sock.accept()
            print("Connected with the Client")
            break
        self.sock.settimeout(3)
        self.auth()
    
    def auth(self):
        self.conn = Connect(self.c)
        self.Auth = serverAuth(self.conn)
        opt = self.conn.recvData()
        
        while True:
            out = False
            if opt == "login":
                out = self.Auth.login()
            else:
                out = self.Auth.register()
            
            if out:
                break
    
    def __del__(self):
        #self.c.close()
        self.sock.close()

if __name__ == "__main__":
    s = Server()