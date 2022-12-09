import socket 
from connection import *
from connect import *

class Server:
    def __init__(self):
        # Wait and listen for client connection
        port = input("Enter hosting port number: ")
        print("Waiting for a connection...")
        self.sock = socket.socket()
        port = int(port)
        while True:
            try:
                self.sock.bind(('', port))
                print("Binded to port: " + str(port))
                break
            except:
                port = port + 1
                continue
        self.sock.listen(5)

        while True:
            self.c, addr = self.sock.accept()
            print("Connected with the Client")
            break
        # Set timeout for blocking socket calls
        self.sock.settimeout(3)

        self.username = ""
        self.auth()
    
    # Method to authenticate client
    def auth(self):
        self.conn = Connect(self.c)
        self.Auth = serverAuth(self.conn)
        # Check whether client wants to login/register
        opt = self.conn.recvData()
        
        while True:
            out = False
            if opt == "login":
                out = self.Auth.login()
            else:
                out = self.Auth.register()
            
            if out:
                break
        
        # Get logged in username
        self.username = self.Auth.getUser()
    
    def __del__(self):
        self.sock.close()

if __name__ == "__main__":
    s = Server()