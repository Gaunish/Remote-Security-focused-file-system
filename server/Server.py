import socket
import logging
import os
import sys
from os import path
from command import LinuxCommand
from auth import User
from pathlib import Path
sys.path.append(os.path.join(Path(sys.path[0]).parent,'common'))
from connection import *
from connect import *

"""
Valid commands: get, put, delete, quit, ls, cd, pwd, mkdir
"""
class Parser:
    def __init__(self) -> None:
        pass

    def checkNArguments(self, input, keyword, n) -> str:  
        words = input.split()
        if (len(words)!=n):
            return 'unknown'
        if words[0] == keyword:
            return keyword
        else:
            return 'unknown'

    """
    Parse the user input and return a flag string indicating type of this command
    Return: linux_cmd(includes ls, cd, mkdir, pwd), get, put, delete, quit, unknown
    """
    def parse(self, input) -> str:
        if input.startswith('ls') or input.startswith('mkdir'):            
            return 'linux_cmd'
        elif input.startswith('pwd'):
            return 'pwd'
        elif input.startswith('cd'):
            return 'cd'
        elif input.startswith('get'):            
            # Syntax: get filename        
            return self.checkNArguments(input, 'get', 2)
        elif input.startswith('put'):
            # Systax: put filename
            return self.checkNArguments(input, 'put', 2)
        elif input.startswith('delete'):
            # Syntax: delete filename
            return self.checkNArguments(input, 'delete', 2)
        elif input.startswith('quit'):
            # Syantax: quit
            return 'quit'
        else:
            return 'unknown'

# Server controller class
class Server:
    def __init__(self, portNum, parser) -> None:
        self.parser = parser
        self.username = ''
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(("",portNum))                   
        self.base_dir = os.path.join(os.path.expanduser('~'), 'ftp')
        self.preparePath(self.base_dir)        
        logging.basicConfig(filename=None, level=logging.INFO, filemode='a', format='%(asctime)s - %(message)s')

    def start(self) -> None:
        while True:
            logging.info('Waiting for connection...')
            # socket start listening
            self.s.listen()
            (self.conn, self.c_addr) = self.s.accept()    
            self.s.settimeout(3)        
            logging.info('Got connection from %s: %d' % (self.c_addr[0], self.c_addr[1]))
            # self.connect = Connect(self.conn)

            while True:            
                if self.username=='':
                    # Request for login/register                    
                    # set username, switch dir to the user root directory                    
                    self.auth()

                    # self.user.username = 'sample_user1' # TODO remove this line
                    logging.info('User '+self.username+' has logged in.')
                    self.user_dir = self.username
                    self.preparePath(os.path.join(self.base_dir, self.user_dir))                
                    logging.info("Current user: " + self.username)
                    self.sendOutputToClient('Hello '+self.username)  
                    os.chdir(os.path.join(self.base_dir, self.user_dir))
                    # print(os.getcwd())
                else:                              
                    # Running state machine
                    cmd_str = self.recvInputFromClient()
                    cmd_str_list = cmd_str.split()
                    logging.info('Command received: '+cmd_str)
                    flag = self.parser.parse(cmd_str)
                    if flag=='unknown':                    
                        self.sendOutputToClient('Invalid command.')
                    elif flag=='linux_cmd':
                        cmd = LinuxCommand(cmd_str)
                        result = cmd.execute()   
                        if result=='':
                            result = ' '                    
                        self.sendOutputToClient(result)
                    elif flag=='pwd':
                        self.sendOutputToClient(self.user_dir)
                    elif flag=='cd':
                        try:
                            temp_dir = cmd_str.split()[1]
                            os.chdir(temp_dir)
                            newdir = os.getcwd()
                            if (len(newdir) > len(self.base_dir) and os.path.join(self.base_dir, self.user.getUser()) in newdir):                                                    
                                self.user_dir = os.getcwd()[len(self.base_dir)+1:]
                                self.sendOutputToClient('Current directory: '+self.user_dir)
                            else:
                                os.chdir(path.join(self.base_dir, self.user_dir))
                                raise FileNotFoundError
                        except FileNotFoundError:
                            self.sendOutputToClient('Directory not found.')
                        except:
                            self.sendOutputToClient("Internal Error occurred.")
                    elif flag=='quit':
                        self.username = ''
                        self.sendOutputToClient('QUITTIUQ')
                        self.conn.close()
                        break;
                    elif flag=='put':                        
                        response = 'waitingforfileupload14235 '+cmd_str_list[1]
                        self.sendOutputToClient(response)
                        self.recvFileFromClient(cmd_str_list[1])
                    elif flag=='get':                        
                        if path.isfile(cmd_str_list[1]):
                            self.sendOutputToClient("6c1993b120701165c72983b9c624f88f")
                            self.sendFileToClient(cmd_str_list[1])
                        else:
                            self.sendFileToClient("File %s not found." % cmd_str_list[1])
                    elif flag=='delete':
                        filename = cmd_str.split()[1]
                        cmd = LinuxCommand('rm '+filename)
                        result = cmd.execute()
                        if result=='':
                            result = "Deletion complete"
                        self.sendOutputToClient(result)
    
    def sendOutputToClient(self, content) -> None:
        self.conn.send(content.encode())
        # self.connect.sendData(content.encode())

    def recvInputFromClient(self) -> str:
        input = self.conn.recv(4096)
        # input = self.connect.recvData()
        return input.decode()

    def sendFileToClient(self, filename) -> None:
        with open(filename, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(4096)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in 
                # busy networks
                self.conn.sendall(bytes_read)

    def recvFileFromClient(self, filename) -> None:
        BLOCK_SIZE = 4096
        with open(filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = self.conn.recv(BLOCK_SIZE)
                # print(len(bytes_read))                
                # write to the file the bytes we just received
                f.write(bytes_read)   
                if len(bytes_read) < BLOCK_SIZE:   # buggy, what if exactly BLOCK_SIZE? 
                    # nothing is received
                    # file transmitting is done
                    # print('break')
                    break                           


    def preparePath(self, target) -> None:
        if not os.path.exists(target):
            os.mkdir(target)
            logging.info('New directory ['+target+'] is created.')

    # Method to authenticate client
    def auth(self):
        self.c = Connect(self.conn)
        self.Auth = serverAuth(self.c)
        # Check whether client wants to login/register
        opt = self.c.recvData()
        
        while True:
            out = False
            if opt == "login":
                out = self.Auth.login()
            else:
                out = self.Auth.register()
            
            if out:
                break
        
        # Get logged in username
        self.username = self.Auth.getUser()


def main():
    port = input("Enter hosting port number: ")
    s = Server(int(port), Parser())
    s.start()

if __name__ == "__main__":
    main()