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
        self.start()

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

    def start(self):
        c = self.sock
        while True:
            output = c.recv(2048).decode()  
            # output = connect.recvData().decode() 
            if (output=='QUITTIUQ'):
                print('User log out. Bye bye!')
                c.close()
                break
            elif (output.startswith('waitingforfileupload14235')): # client must make sure the file exists before sending it
                filename = output.split()[1]              
                with open(filename, "rb") as f:
                    while True:
                        # read the bytes from the file
                        bytes_read = f.read(4096)
                        if not bytes_read:
                            # file transmitting is done
                            break
                        # we use sendall to assure transimission in 
                        # busy networks
                        c.sendall(bytes_read)        
            elif output=='6c1993b120701165c72983b9c624f88f':
                BLOCK_SIZE = 4096
                with open(filename, "wb") as f:
                    while True:
                        # read 1024 bytes from the socket (receive)
                        bytes_read = c.recv(BLOCK_SIZE)
                        # print(len(bytes_read))                
                        # write to the file the bytes we just received
                        f.write(bytes_read)   
                        if len(bytes_read) < BLOCK_SIZE:   # buggy, what if exactly BLOCK_SIZE? 
                            # nothing is received
                            # file transmitting is done
                            # print('break')
                            break      
            else:
                print(output)
            user_input = input('Input your command:\n') # we trust client that the put file exists
            c.send(user_input.encode())
            # connect.sendData(user_input.encode())

    def __del__(self):
        self.sock.close()

if __name__ == "__main__":
    c = Client()