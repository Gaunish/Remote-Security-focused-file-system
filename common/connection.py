import bcrypt
import random
import socket
from Crypto.Cipher import AES
import pyDH

class Connect:

    def __init__(self, sock):
        self.sock = sock
        dif = pyDH.DiffieHellman()
        self.pubKey = dif.gen_public_key()
        self.sock.send(self.pub_key)
        pubKeyClient = self.sock.recv(1024)
        self.sharedKey = dif.gen_shared_key(pubKeyClient)
    
    def sendData(self, data):
        cipher = AES.new(self.sharedKey, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        nonce = cipher.nonce
        self.sock.send(nonce)
        self.sock.send(ciphertext)
        self.sock.send(tag)
    
    def recvData(self):
        nonce = self.sock.recv(1024)
        ciphertext = self.sock.recv(10000)
        tag = self.sock.recv(1024)
        cipher = AES.new(self.sharedKey, AES.MODE_EAX, nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)
        return data
        '''
        option = socket.recv(20)
        if option == "login":
            login()
        else:
            register()
    
    def login(self):
        print "hi"
    
    def register(self):
'''
    