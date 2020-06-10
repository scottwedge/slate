import socket
import keyboard

from socketWrappers import connect, sendPacket, getPacket
import struct
import config as cfg

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


class Client:
    def __init__(self):

        self.username = getUsername()
        self.connectToServ()

    def connectToServ(self):
        while True:
            ip=input("What IP Would You Like to Connect to: ")
            ip = ip.strip()
            if ip == cfg.closePhrase:
                return
            try:
                sock = connect(ip)
                sent = sendPacket(sock,False, self.username)

                if not sent:
                    print("Failed to Communicate With Server")
                    sock.close()
                    continue

                self.sock = sock
                self.serverActive = True
                return
            except:
                print("Can't Connect to IP")

    def disconnect(self):
        sendPacket(self.sock,True,"")
        self.sock.close()

    def messaging(self):
        message = input(self.username+"> ")

        eot=False
        if message == cfg.closePhrase:
            eot=True
            self.serverActive = False

        sent = sendPacket(self.sock,eot,message)
        if not sent:
            print("Server Disconnected")
            self.serverActive=False

    def parseNextPacket(self):
        try:
            eot,username,message = getPacket(self.sock)
            # checks eot
            if eot:
                self.serverActive = False
                print(message)
            else:
                print(f"{username}> {message}")
        except:
            pass



if __name__ == "__main__":
    client=Client()
    while client.serverActive:
        if keyboard.is_pressed(cfg.typeHotkey):
            client.messaging()
        client.parseNextPacket()
