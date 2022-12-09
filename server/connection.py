import bcrypt
import random
import socket
from Crypto.Cipher import AES
import pyDH, time
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
        self.write.flush()
        self.write.write(ascii(23))
        self.write.write('\n')
        self.write.flush()
    
    def recv(self):
        out = ""
        while True:
            data = self.read.readline()
            data = data.strip()
            if data == ascii(23):
                break
            if data:
                out += data
        return out

    def sendNonByte(self, data):
        #self.send("nonByte")
        cipher = AES.new(self.sharedKey, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(str(data).encode())
        self.sendData(cipher, ciphertext, tag)
    
    def sendByte(self, data):
        #self.send("Byte")
        cipher = AES.new(self.sharedKey, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        self.sendData(cipher, ciphertext, tag)

    def sendb(self, data):
        self.sock.sendall(data)
        '''
        if doWait:
            time.sleep(4)
        else:
            time.sleep(2)
        '''
        #time.sleep(1)

    def recvb(self):
        timeout = time.time() + 0.001
        out = bytes()
        while True:
            try:
                recvdata = self.sock.recv(1024)
            except:
                print("Connection timed out")
                break
            out += recvdata
            if not recvdata or time.time() > timeout:
                break
            print("out: " + str(out))
        print("---x--x-x-x-x--xx-x-")
        return out

    def sendData(self, cipher, ciphertext, tag):
        nonce = cipher.nonce
        print(nonce)
        print(ciphertext)
        print(tag)
        '''
        self.send(nonce.decode("ISO-8859-1"))
        self.send(ciphertext.decode("ISO-8859-1"))
        self.send(tag.decode("ISO-8859-1"))
        '''
        combined = nonce + b'\x1f\x19\x13\x09\x32' + ciphertext + b'\x1f\x19\x13\x09\x32' + tag
        self.sendb(combined)
        #self.sendb(nonce, True)
        #self.sendb(ciphertext, True)
        #self.sendb(tag, False)
        
    
    def recvData(self):
        #type = self.recv()
        '''
        nonce = self.recv().encode("ISO-8859-1")
        ciphertext = self.recv().encode("ISO-8859-1")
        tag = self.recv().encode("ISO-8859-1")
        '''
        out = self.recvb().split(b'\x1f\x19\x13\x09\x32')
        nonce = out[0]
        ciphertext = out[1]
        tag = out[2]
        print("-----------------------")
        print(nonce)
        print(ciphertext)
        print(tag)
        cipher = AES.new(self.sharedKey, AES.MODE_EAX, nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)

        #if type == "nonByte":
        data = str(data.decode())
        print("data: " + str(data))
        return data
    