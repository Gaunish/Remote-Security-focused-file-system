import socket
import threading
import sys
import unittest
sys.path.append('../server')
from Server import Server, Parser

def testServerOps(s) -> None:
    s.start()
    s.sendOutputToClient("Test message from server")
    print(s.recvInputFromClient())

"""
Test connection of server. SendOutput/RecvInput

"""
def testServer():
    # ip = '67.159.94.23'
    ip = '127.0.0.1'
    port = 9988
    s = Server(port, Parser())

    t = threading.Thread(target=s.start)
    t.start()

    c = socket.socket()
    c.connect((ip, port))
    print('Test Client: '+c.recv(1024).decode())  
    c.send('Test message from client'.encode());
    print('Test Client: '+c.recv(1024).decode())  
    c.send('ls -l'.encode())
    print('Test Client: '+c.recv(1024).decode())  
    print('Test Client: '+c.recv(1024).decode())  
    c.send('ls -l exhoso'.encode())
    print('Test Client: '+c.recv(1024).decode())      
      
    c.close()

testServer()

"---------------------------------------"
"""
"""
class TestParser(unittest.TestCase):      
    def testCheck2Arguments(self):
        p = Parser()
        self.assertEqual(p.check2Arguments('get good', 'get'), 'get')
        self.assertEqual(p.check2Arguments('get  good', 'get'), 'get')
        self.assertNotEqual(p.check2Arguments('getgood', 'get'), 'get')

    def testParse(self):
        p = Parser()        
        self.assertEqual('linux_cmd', p.parse('cd exo'))
        self.assertEqual('linux_cmd', p.parse('ls'))
        self.assertEqual('linux_cmd', p.parse('pwd'))
        self.assertEqual('linux_cmd', p.parse('mkdir superman'))
        self.assertEqual('get', p.parse('get file'))
        self.assertEqual('put', p.parse('put file'))
        self.assertEqual('delete', p.parse('delete file'))
        self.assertEqual('quit', p.parse('quit'))
        self.assertEqual('unknown', p.parse('shoot'))

# unittest.main()