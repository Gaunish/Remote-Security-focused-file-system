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
        out = self.auth.register(username, password)
        self.conn.sendData(str(out))
        return out

    def login(self):
        username = self.conn.recvData()
        clientNonce = self.conn.recvData()
        serverNonce = secrets.token_urlsafe()
        Nonce = clientNonce + serverNonce
        salt = self.auth.getSalt(username)

        if salt == None:
            return False
        
        self.conn.sendData(salt)
        self.conn.sendData(Nonce)
        proof = self.conn.recvData()
        out = self.auth.login(username, proof, Nonce)
        self.conn.sendData(str(out))
        return out