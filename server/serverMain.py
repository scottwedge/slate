import socket
import keyboard

from socketWrappers import startServer, awaitConnection, send, recieve

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

def serverMessaging(clientSocket, username):
    if keyboard.is_pressed(cfg.typeHotkey):
        message = input(username+"> ")
        send(clientSocket,username+"> "+message)

def serverRecieving(clientSocket):
    #try catch to avoid timeout if no message is sent
    try:
        print(recieve(clientSocket))
    except:
        pass


def mainLoop(clientSocket, username):
    while state.clientConnected:
        serverMessaging(clientSocket, username)
        serverRecieving(clientSocket)


if __name__ == "__main__":
    username = getUsername()

    s = startServer()
    clientSocket = awaitConnection(s)
    mainLoop(clientSocket,username)
    clientSocket.close()