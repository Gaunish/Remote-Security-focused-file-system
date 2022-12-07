import sys
import socket

PORT = 7899
IP = '127.0.0.1'
username = 'sample_user1'

c = socket.socket();
c.connect((IP, PORT))

# skip login fro now

while True:
    output = c.recv(2048).decode()    
    if (output=='QUITTIUQ'):
        print('User log out. Bye bye!')
        c.close()
        break
    else:
        print(output)
    user_input = input('Input your command:\n')
    c.send(user_input.encode())



