import socket
import config as cfg
import state

def startServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = socket.gethostbyname(socket.gethostname())
    s.bind((ip, cfg.port))
    print(f"Server Started with IP: {ip}, and port: {cfg.port}")

    return s

def awaitConnection(s):
    s.listen(cfg.queueLen)

    clientSocket, addr = s.accept()
    print ('Connection address: ', addr)
    state.clientConnected = True
    
    clientSocket.settimeout(cfg.waitTime)
    
    return clientSocket

def send(clientSocket,outMessage):
    try:
        clientSocket.send(bytes(outMessage,cfg.encoding))
    except:
        state.clientConnected = False
        print("Client: Disconnected")


def recieve(clientSocket):

    inMessage = clientSocket.recv(cfg.bufferSize)
    inMessage = inMessage.decode(cfg.encoding)

    return inMessage