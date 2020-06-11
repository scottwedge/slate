import socket
from time import sleep
import config as cfg
import marshal

def getRoomName():
    try:
        file = open("roomName.txt", 'r')

        name = file.readline()
        if not name:
            file = open("roomName.txt", 'w')
            name = input("What Would You Like To Name This Chat Room: ")
            file.write(name)

    except IOError:
        file = open("roomName.txt", 'w')
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
            ip = socket.gethostbyname(socket.gethostname())
            s.bind((ip, cfg.port))
            print(f"Server Started with IP: {ip}, and port: {cfg.port}")
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


