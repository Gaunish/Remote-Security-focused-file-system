import socket 
import secrets
import hmac, hashlib
import bcrypt
from connection import *

class Client:

    def __init__(self):
        self.sock = socket.socket()
        while True:
            server = input("Enter server name: ")
            try:
                self.sock.connect((server, 12345))
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
        password = input("Enter Password: ")
        self.conn.sendNonByte(username)
        return password
    
    def Register(self):
        out = False
        while out != True:
            password = self.getDetails()
            self.conn.sendNonByte(password)
            out = self.conn.recvData()
            if out == "False":
                print("Register failed, Please try again\n")
    
    def Login(self):
        out = False
        while out != True:
            password = self.getDetails()
            userExist = self.conn.recvData()
            if userExist == "False":
                print("username doesn't exist, Please try again\n")
                continue

            self.conn.sendNonByte(secrets.token_urlsafe()) 
            salt = self.conn.recvData()
            nonce = self.conn.recvData()
            passwd = bcrypt.hashpw(str(password).encode('utf-8'), salt.encode('utf-8')).decode()
            h = hmac.new(nonce, passwd, hashlib.sha256)
            proof = h.hexdigest().decode()
            self.conn.sendNonByte(proof)

            out = self.conn.recvData()
            if out == "False":
                print("Login failed, Please try again\n")

    def __del__(self):
        self.sock.close()

if __name__ == "__main__":
    c = Client()