import socket
import keyboard

from socketWrappers import connect, send, recieve

import config as cfg
import state

def getUsername():
    try:
        file = open("username.txt", 'r')

        username = file.readline()
        if not username:
            file = open("username.txt", 'w')
            username = input("Hello New User, Whats Your Name: ")
            file.write(username)

        username = file.readline()

    except IOError:
        file = open("username.txt", 'w')
        username = input("Hello New User, Whats Your Name: ")
        file.write(username)

    return username


def clientMessaging(s, username):
    if keyboard.is_pressed(cfg.typeHotkey):
        message = input(username+"> ")
        send(s,message)

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
