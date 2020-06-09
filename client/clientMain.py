import socket
import keyboard

from socketWrappers import connect, send, recieve

import config as cfg
import state

def getUsername():
    try:
        file = open("usernames.txt", 'r')

        if not file:
            raise Exception("file empty")

        username = file.readline()

    except IOError:
        file = open("usernames.txt", 'w')
        username = input("Hello New User, Whats Your Name: ")
        file.write(username)

    return username


def clientMessaging(s, username):
    if keyboard.is_pressed(cfg.typeHotkey):
        message = input(username+"> ")
        send(s,username+"> "+message)

def clientRecieving(s):
    #try catch to avoid timeout if no message is sent
    try:
        print(recieve(s))
    except:
        pass

def mainLoop(s, username):
    while state.serverActive:
        clientMessaging(s, username)
        clientRecieving(s)

if __name__ == "__main__":
    username = getUsername()

    s = connect(username)
    mainLoop(s,username)
    s.close()
