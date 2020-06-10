import socket
from time import sleep
import config as cfg

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
        




def send(clientSocket,outMessage):
    clientSocket.send(bytes(outMessage,cfg.encoding))



def recieve(clientSocket):

    inMessage = clientSocket.recv(cfg.bufferSize)
    inMessage = inMessage.decode(cfg.encoding)

    return inMessage