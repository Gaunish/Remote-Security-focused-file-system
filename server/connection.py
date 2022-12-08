import bcrypt
import random
import socket
from Crypto.Cipher import AES
import pyDH
from Crypto.Protocol.KDF import PBKDF2

class Connect:

    def __init__(self, sock):
        self.sock = sock
        self.read = self.sock.makefile('r',)
        self.write = self.sock.makefile('w')
        dif = pyDH.DiffieHellman()
        self.pubKey = dif.gen_public_key()
        self.send(str(self.pubKey))
        pubKeyClient = int(self.recv())
        self.sharedKey = dif.gen_shared_key(pubKeyClient)
        self.sharedKey = PBKDF2(self.sharedKey, self.sharedKey, dkLen=32)
    
    def send(self, data):
        self.write.write(data)
        self.write.write('\n')
        self.write.write(ascii(23) + '\n')
        self.write.flush()
    
    def recv(self):
        out = ""
        while True:
            data = self.read.readline()
            data = data.strip()
            if not data or data == ascii(23):
                break
            out += data
        return out

    def sendNonByte(self, data):
        self.send("nonByte")
        cipher = AES.new(self.sharedKey, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(str(data).encode())
        self.sendData(cipher, ciphertext, tag)
    
    def sendByte(self, data):
        self.send("Byte")
        cipher = AES.new(self.sharedKey, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        self.sendData(cipher, ciphertext, tag)

    def sendData(self, cipher, ciphertext, tag):
        nonce = cipher.nonce
        #print(nonce)
        #print(ciphertext)
        #print(tag)
        self.send(nonce.decode("ISO-8859-1"))
        self.send(ciphertext.decode("ISO-8859-1"))
        self.send(tag.decode("ISO-8859-1"))
    
    def recvData(self):
        type = self.recv()
        nonce = self.recv().encode("ISO-8859-1")
        ciphertext = self.recv().encode("ISO-8859-1")
        tag = self.recv().encode("ISO-8859-1")
        #print(nonce)
        #print(ciphertext)
        #print(tag)
        cipher = AES.new(self.sharedKey, AES.MODE_EAX, nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)

        if type == "nonByte":
            data = str(data.decode())
        print("data: " + str(data))
        return data
    