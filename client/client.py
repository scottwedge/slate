import socket
import keyboard
from time import sleep

from helpers import connect, sendPacket, getPacket, getUsername
import threads
import struct
import config as cfg

class Client:
    def __init__(self):

        self.username = getUsername()
        self.connectToServ()

        self.threads=[]

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
                self.running = True
                return
            except:
                print("Can't Connect to IP")

    def disconnect(self):
        sendPacket(self.sock,True,"")
        self.sock.close()

    def sending(self):
        while self.running:
            if keyboard.is_pressed(cfg.typeHotkey):
                message = input(self.username+"> ")
                eot=False
                if message == cfg.closePhrase:
                    eot=True
                    self.running = False

                sent = sendPacket(self.sock,eot,message)
                if not sent:
                    print("Server Disconnected")
                    self.running=False

    def recieving(self):
        while self.running:
            try:
                eot,username,message = getPacket(self.sock)
                # checks eot
                if eot:
                    self.running = False
                    print(message)
                else:
                    print(f"{username}> {message}")
            except:
                print("Server Disconnected")
                self.running = False





if __name__ == "__main__":
    client=Client()
    threads.startThreads(client)
    while client.running:
        sleep(10)
