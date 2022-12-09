import bcrypt
import random
import secrets
from auth import *

class serverAuth:
    
    def __init__(self, conn):
        self.conn = conn
        self.auth = User()
    
    def register(self):
        username = self.conn.recvData()
        password = self.conn.recvData()
        out = self.auth.DBregister(username, password)
        print(out)
        self.conn.sendNonByte(out)
        return out

    def login(self):
        username = self.conn.recvData()
        salt = self.auth.getSalt(username)
        print("salt: " + str(salt))
        if salt == None:
            self.conn.sendNonByte("False")
            return False
        self.conn.sendNonByte("True")

        self.conn.sendNonByte(salt)
        clientNonce = self.conn.recvData()
        serverNonce = secrets.token_urlsafe()
        Nonce = clientNonce + serverNonce 
        print("salt: " + salt)
        print("nonce: " + Nonce)
        self.conn.sendNonByte(Nonce)
        '''
        proof = self.conn.recvData()
        out = self.auth.DBlogin(username, proof, Nonce)
        
        self.conn.sendNonByte(str(out))
        '''
        return False