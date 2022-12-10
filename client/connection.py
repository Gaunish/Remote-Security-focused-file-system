import bcrypt
import random
import socket
from Crypto.Cipher import AES
import pyDH, time
from Crypto.Protocol.KDF import PBKDF2

# SAME AS server/connection.py
class Connect:
    # Recieve socket from program
    def __init__(self, sock):
        self.sock = sock
        # Open file read,write for Diffie-Hellman, non-encrypted
        self.read = self.sock.makefile('r',)
        self.write = self.sock.makefile('w')
        # Initiate Diffie-Hellman/ DH
        dif = pyDH.DiffieHellman()
        # Generate own DH Key
        self.pubKey = dif.gen_public_key()
        self.sendUnEnc(str(self.pubKey))
        # Recieve other key
        pubKeyClient = int(self.recvUnEnc())
        # Generate and Hash shared Key for future encryption
        self.sharedKey = dif.gen_shared_key(pubKeyClient)
        self.sharedKey = PBKDF2(self.sharedKey, self.sharedKey, dkLen=32)
    
    # Method to send UnEncrypted data
    def sendUnEnc(self, data):
        self.write.write(data)
        self.write.write('\n')
        self.write.flush()
        # send delim to signify end of transmission
        self.write.write(ascii(23))
        self.write.write('\n')
        self.write.flush()

    # Method to recv UnEncrypted data
    def recvUnEnc(self):
        out = ""
        # wait till all data is received
        while True:
            data = self.read.readline()
            data = data.strip()
            # Got Delim, break
            if data == ascii(23):
                break
            if data:
                out += data
        return out

    # NOTE: User API to send data
    # Method to send data after Encryption
    def sendData(self, data):
        # using AES-256 Mode EAX, encrypt data 
        cipher = AES.new(self.sharedKey, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(str(data).encode())
        self.sendEnc(cipher, ciphertext, tag)
    
    def sendEnc(self, cipher, ciphertext, tag):
        time.sleep(1)
        nonce = cipher.nonce
        # Combine Encryption components with delim in between
        combined = nonce + b'\x1f\x19\x13\x09\x32' + ciphertext + b'\x1f\x19\x13\x09\x32' + tag
        self.sock.sendall(combined)
        time.sleep(0.2)

    # Recieve Encrypted data
    def recvEnc(self):
        # Use timeout to recieve data in short time window
        timeout = time.time() + 0.001
        # output variable
        out = bytes()
        while True:
            # Recieve data, if stuck
            # timeout after 3 seconds
            try:
                recvdata = self.sock.recv(1024)
            except:
                # Return any captured data
                print("Connection timed out, Re-establishing...")
                break
            # Add recieve data chunk to output
            out += recvdata
            # If timeout or empty data, break
            if not recvdata or time.time() > timeout:
                break
        return out
    
    # NOTE: User API to recieve data
    def recvData(self):
        # split recieved data based on delim
        out = self.recvEnc().split(b'\x1f\x19\x13\x09\x32')
        nonce = out[0]
        ciphertext = out[1]
        tag = out[2]

        # Decrypt and verify the encrypted data
        cipher = AES.new(self.sharedKey, AES.MODE_EAX, nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)

        # Decode the bytes to string
        data = str(data.decode())
        time.sleep(0.9)
        return data