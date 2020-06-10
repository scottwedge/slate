import socket
import config as cfg
import marshal

def connect(ip):
    ip.strip()
    #ipv4 socket using tcp
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #connect to server
    sock.connect((ip, cfg.port))
    sock.settimeout(cfg.waitTime)
    return sock

def sendPacket(sock, eot, message):
    try:
        packet = marshal.dumps((eot,bytes(message,cfg.encoding)))
        sock.send(packet)
        return True
    except:
        return False

def getPacket(sock):
    packet = sock.recv(cfg.bufferSize)
    eot,username,text = marshal.loads(packet)
    username = username.decode(cfg.encoding)
    text = text.decode(cfg.encoding)
    return eot,username,text