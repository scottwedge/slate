import socket

import config as cfg

def startServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = socket.gethostbyname(socket.gethostname())
    s.bind((ip, cfg.port))
    print(f"Server Started with IP: {ip}, and port: {cfg.port}")
    s.listen(cfg.queueLen)
    return s



def send(clientSocket,outMessage):
    clientSocket.send(bytes(outMessage,cfg.encoding))



def recieve(clientSocket):

    inMessage = clientSocket.recv(cfg.bufferSize)
    inMessage = inMessage.decode(cfg.encoding)

    return inMessage