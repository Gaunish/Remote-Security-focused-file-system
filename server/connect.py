import bcrypt
import random
import secrets
from auth import *

# Class to authenticate user via connection
class serverAuth:
    
    def __init__(self, conn):
        self.conn = conn
        self.auth = User()
        
    # Return username, if user is logged in
    # else empty string
    def getUser(self):
        return self.auth.getUser()

    def register(self):
        username = self.conn.recvData()
        password = self.conn.recvData()
        # Check with Database API, if successful
        out = self.auth.DBregister(username, password)
        # Send the result
        self.conn.sendData(out)
        return out

    def login(self):
        username = self.conn.recvData()
        # check if username exist, by retrieving salt
        # send output, salt to client
        salt = self.auth.getSalt(username)
        if salt == None:
            self.conn.sendData("False")
            return False
        self.conn.sendData("True")
        self.conn.sendData(salt)

        # Recieve client Nonce, send combined Nonce
        clientNonce = self.conn.recvData()
        serverNonce = secrets.token_urlsafe()
        Nonce = clientNonce + serverNonce 
        self.conn.sendData(Nonce)

        # Recieve HMAC password
        proof = self.conn.recvData()
        # authenticate with Database APIw
        out = self.auth.DBlogin(username, proof, Nonce)
        # Send output to client
        self.conn.sendData(str(out))
        return out

    