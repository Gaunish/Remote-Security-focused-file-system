import socket 
import secrets
import hmac, hashlib
from common.connection import *

class Client:

    def __init__(self):
        self.sock = socket.socket()
        server = input("Enter server name: ")
        self.sock.connect((server, 1234))
        self.conn = Connect(self.sock)
        self.auth()

    def auth(self):
        option = 0
        while option != 1 or option != 2: 
            option = input("Please Enter:\n(1) for Login\n(2) for Register\n")
        
        if option == 1:
            self.conn.sendData("login")
            self.Login()
        else:
            self.conn.sendData("register")
            self.Register()
    
    def getDetails(self):
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        self.conn.sendData(username)
        return password
    
    def Register(self):
        out = False
        while out != True:
            password = self.getDetails()
            self.conn.sendData(password)
            out = self.conn.recvData()
    
    def Login(self):
        out = False
        while out != True:
            password = self.getDetails()
            self.conn.sendData(secrets.token_urlsafe())
            salt = self.conn.recvData()
            nonce = self.conn.recvData()
            passwd = bcrypt.hashpw(str(password).encode('utf-8'), salt.encode('utf-8')).decode()
            h = hmac.new(nonce, passwd, hashlib.sha256)
            proof = h.hexdigest().decode()
            self.conn.sendData(proof)
            out = self.conn.recvData()

    def __del__(self):
        self.sock.close()