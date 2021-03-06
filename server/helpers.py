import socket
from time import sleep
import marshal
from urllib.request import urlopen

import server.config as cfg

def getRoomName():
    try:
        file = open(cfg.roomNamePath, 'r')

        name = file.readline()
        if not name:
            file = open(cfg.roomNamePath, 'w')
            name = input("What Would You Like To Name This Chat Room: ")
            file.write(name)

    except IOError:
        file = open(cfg.roomNamePath, 'w')
        name = input("What Would You Like To Name This Chat Room: ")
        file.write(name)
    print(f"Server Name: {name}")
    return name


#-------------------#
#  Socket Wrappers  #
#-------------------#
def startServer():
    #waits for server to close before restarting
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            externalIp = urlopen('https://api.ipify.org').read().decode('utf8')
            internalIp = socket.gethostbyname(socket.gethostname())

            s.bind(("", cfg.port))
            print(f"Server Started with external IP: {externalIp}, internal IP {internalIp}, and port: {cfg.port}")
            s.listen(cfg.queueLen)
            return s
        except:
            sleep(1)


#server packet formatting 
# eot - bool notifying server is closing
# username - username of messanger
# message - text to be displaied
def sendPacket(sock,eot,userListFlag,username,message):
    packet = marshal.dumps( (eot, userListFlag,
                        bytes(username,cfg.encoding),
                        bytes(message,cfg.encoding)) )

    sock.send(packet)

def getPacket(sock):
    packet = sock.recv(cfg.bufferSize)
    eot,Text = marshal.loads(packet)
    Text = Text.decode(cfg.encoding)

    return eot,Text


