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
        self.conn.sendNonByte(str(out))
        return out

    def login(self):
        username = self.conn.recvData()
        salt = self.auth.getSalt(username)
        if salt == None:
            self.conn.sendNonByte("False")
            return False
        self.conn.sendNonByte("True")

        clientNonce = self.conn.recvData()
        serverNonce = secrets.token_urlsafe()
        Nonce = clientNonce + serverNonce        
        self.conn.sendNonByte(salt)
        self.conn.sendNonByte(Nonce)
        proof = self.conn.recvData()
        out = self.auth.DBlogin(username, proof, Nonce)
        
        self.conn.sendNonByte(str(out))
        return out