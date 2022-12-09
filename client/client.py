import socket 
import secrets
import hmac, hashlib
import bcrypt
from connection import *

class Client:

    def __init__(self):
        self.username = None
        self.sock = socket.socket()
        self.sock.settimeout(3)
        while True:
            server = input("Enter server name: ")
            try:
                self.sock.connect((server, 3002))
                self.conn = Connect(self.sock)

                break
            except:
                print("Connection to server " + server + " failed. Please try again.\n")
                continue
        self.auth()

    def auth(self):
        option = 0
        while True: 
            try:
                option = int(input("Please Enter:\n(1) for Login\n(2) for Register\n"))
                if option == 1 or option == 2:
                    break
            except:
                print("\nWrong input type. Required int, Please try again\n") 
               
        if option == 1:
            self.conn.sendNonByte("login")
            self.Login()
        else:
            self.conn.sendNonByte("register")
            self.Register()
    
    def getDetails(self):
        username = input("Enter Username: ")
        self.conn.sendNonByte(username)
        return username
    
    def Register(self):
        out = False
        while out != True:
            username = self.getDetails()
            password = input("Enter Password: ")
            self.conn.sendNonByte(password)
            out = self.conn.recvData()
            if out == "False":
                print("Register failed, Please try again\n")
                continue
            else:
                self.username = username
                break
    
    def Login(self):
        out = False
        while out != True:
            username = self.getDetails()
            userExist = self.conn.recvData()
            if userExist == "False":
                print("username doesn't exist, Please try again\n")
                continue
            
            password = input("Enter Password: ")
            ClientNonce = secrets.token_urlsafe()
            print("ClientNonce:" + ClientNonce)
            self.conn.sendNonByte(ClientNonce) 
            salt = self.conn.recvData()
            nonce = self.conn.recvData()
            print("salt: " + salt)
            print("nonce: " + nonce)
            '''
            passwd = bcrypt.hashpw(str(password).encode('utf-8'), salt.encode('utf-8')).decode()
            h = hmac.new(nonce, passwd, hashlib.sha256)
            proof = h.hexdigest().decode()
            self.conn.sendNonByte(proof)

            out = self.conn.recvData()
            '''
            out = False
            if out == "False":
                print("Login failed, Please try again\n")
            else:
                self.username = username
                break

    def __del__(self):
        self.sock.close()

if __name__ == "__main__":
    c = Client()