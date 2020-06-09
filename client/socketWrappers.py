import socket
import config as cfg
import state

def connect(username):
    ip=input("What IP Would You Like to Connect to: ")
    ip.strip()

    #ipv4 socket using tcp
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    

    #connect to server
    s.connect((ip, cfg.port))
    state.serverActive=True
    send(s, username)
    s.settimeout(cfg.waitTime)
    return s

def send(s,message):
    try:
        s.send(bytes(message,cfg.encoding))
    except:
        state.serverActive = False
        print("Server Closed")
    
def recieve(s):
    inMessage = s.recv(cfg.bufferSize)
    inMessage = inMessage.decode(cfg.encoding)
    return inMessage