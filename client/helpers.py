import socket
import client.config as cfg

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