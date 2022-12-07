import socket
import logging
import os
from os import path
from command import LinuxCommand
from auth import User

PORT = 7899

"""
Valid commands: get, put, delete, quit, ls, cd, pwd, mkdir
"""
class Parser:
    def __init__(self) -> None:
        pass

    def check2Arguments(self, input, keyword) -> str:  
        words = input.split()
        if (len(words)!=2):
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
            return self.check2Arguments(input, 'get')
        elif input.startswith('put'):
            # Systax: put filename
            return self.check2Arguments(input, 'put')
        elif input.startswith('delete'):
            # Syntax: delete filename
            return self.check2Arguments(input, 'delete')
        elif input.startswith('quit'):
            # Syantax: quit
            return 'quit'
        else:
            return 'unknown'

# Server controller class
class Server:
    def __init__(self, portNum, parser) -> None:
        self.parser = parser
        self.user = User()
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
            logging.info('Got connection from %s: %d' % (self.c_addr[0], self.c_addr[1]))

            while True:            
                if self.user.getUser()=='':
                    # Request for login/register
                    # TODO tiny state machine managing 
                    # set username, switch dir to the user root directory
                    # TODO register or login
                    self.user.username = 'sample_user1' # TODO remove this line
                    logging.info('User '+self.user.getUser()+' has logged in.')
                    self.user_dir = self.user.getUser()
                    self.preparePath(os.path.join(self.base_dir, self.user_dir))                
                    logging.info("Current user: " + self.user.getUser())
                    self.sendOutputToClient('Hello '+self.user.getUser())  
                    os.chdir(os.path.join(self.base_dir, self.user_dir))
                    print(os.getcwd())
                else:                              
                    # Running state machine
                    cmd_str = self.recvInputFromClient()
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
                        self.user = User()
                        self.sendOutputToClient('QUITTIUQ')
                        self.conn.close()
                        break;
                    else:
                        # TODO execute commands and return its output
                        pass
    
    def sendOutputToClient(self, content) -> None:
        self.conn.send(content.encode())

    def recvInputFromClient(self) -> str:
        input = self.conn.recv(4096)
        return input.decode()

    def sendFileToClient(self, filename) -> None:
        # TODO
        pass

    def recvFileFromClient(self) -> None:
        # TODO
        pass

    def preparePath(self, target) -> None:
        if not os.path.exists(target):
            os.mkdir(target)
            logging.info('New directory ['+target+'] is created.')


def main():
    s = Server(PORT, Parser())
    s.start()

if __name__ == "__main__":
    main()