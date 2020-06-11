import socket
import config as cfg
import marshal
def getUsername():
    try:
        file = open("username.txt", 'r')

        username = file.readline()
        if not username:
            file = open("username.txt", 'w')
            username = input("Hello New User, Whats Your Name: ")
            file.write(username)


    except IOError:
        file = open("username.txt", 'w')
        username = input("Hello New User, Whats Your Name: ")
        file.write(username)
    return username

#-------------------#
#  Socket Wrappers  #
#-------------------#
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
    eot,userChange,username,text = marshal.loads(packet)
    username = username.decode(cfg.encoding)
    text = text.decode(cfg.encoding)
    return eot,userChange,username,text