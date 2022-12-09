import socket 
import secrets
import hmac, hashlib
import bcrypt
from connection import *

class Client:

    def __init__(self):
        self.sock = socket.socket()
        # Set timeout for blocking socket calls
        self.sock.settimeout(3)
        while True:
            server = input("Enter server name: ")
            port = input("Enter port number: ")
            try:
                # Connect to server
                print(int(port))
                self.sock.connect((server, int(port)))
                self.conn = Connect(self.sock)
                break
            except:
                print("Connection to server " + server + " failed. Please try again.\n")
                continue

        self.username = ""
        self.auth()

    # Method to authenticate the user 
    def auth(self):
        option = 0
    
        while True: 
            try:
                # Recieve option for register/login
                option = int(input("Please Enter:\n(1) for Login\n(2) for Register\n"))
                if option == 1 or option == 2:
                    break
            except:
                print("\nWrong input type. Required int, Please try again\n") 
        
        if option == 1:
            self.conn.sendData("login")
            self.Login()
        else:
            self.conn.sendData("register")
            self.Register()
    
    # Input username and send it to server
    def inputUsername(self):
        username = input("Enter Username: ")
        self.conn.sendData(username)
        return username
    
    def Register(self):
        out = False
        while out != True:
            username = self.inputUsername()
            # Recive password and send it
            password = input("Enter Password: ")
            self.conn.sendData(password)
            # Check if user is successfully registered
            out = self.conn.recvData()
            if out == "False":
                print("Register failed, Please try again\n")
                continue
            else:
                # indicates user has logged in
                self.username = username
                print("You have succsesfully registered! Welcome..")
                break
    
    def Login(self):
        out = False
        while out != True:
            username = self.inputUsername()
            # Check with server whether username exist
            userExist = self.conn.recvData()
            if userExist == "False":
                print("username doesn't exist, Please try again\n")
                continue
            
            # Recieve salt for password
            salt = self.conn.recvData()
            password = input("Enter Password: ")

            #Send Nonce, recieve combined Nonce
            ClientNonce = secrets.token_urlsafe()
            self.conn.sendData(ClientNonce) 
            nonce = self.conn.recvData()

            # Encrypt password with salt and create HMAC, send it
            passwd = bcrypt.hashpw(str(password).encode('utf-8'), salt.encode('utf-8')).decode()
            h = hmac.new(nonce.encode('utf-8'), passwd.encode('utf-8'), hashlib.sha256)
            proof = h.hexdigest()
            self.conn.sendData(proof)

            # Check if user has succesfully logged in
            out = self.conn.recvData()
            if out == "False":
                print("Login failed, Please try again\n")
            else:
                # indicates user has logged in
                self.username = username
                print("You have succsesfully logged in!")
                break

    def __del__(self):
        self.sock.close()

if __name__ == "__main__":
    c = Client()