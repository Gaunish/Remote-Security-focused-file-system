import sys
import os
import socket
import tqdm
from pathlib import Path
sys.path.append(os.path.join(Path(sys.path[0]).parent,'common'))
from connection import Connect

PORT = 7899
IP = '127.0.0.1'
username = 'sample_user1'

c = socket.socket();
c.connect((IP, PORT))

# skip login fro now

connect = Connect(c)

while True:
    # output = c.recv(2048).decode()  
    output = connect.recvData().decode() 
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
    # c.send(user_input.encode())
    connect.sendData(user_input.encode())



