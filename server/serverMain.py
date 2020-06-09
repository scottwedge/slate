import socket
import keyboard
import threading
from time import sleep
from queue import Queue
from socketWrappers import startServer, send, recieve

import config as cfg


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

class MessageQueue:
    def __init__(self):
        self.queue=Queue()
    def put(self,message, messangerID = -1):
        self.queue.put((message,messangerID))
    def get(self):
        val = self.queue.get()
        return val[0],val[1]
    def empty(self):
        return self.queue.empty()

class Server:
    def __init__(self):
        self.nextClientID = 0
        self.running = True
        self.s = startServer()

        self.username = getUsername()

        self.clientUsernames=[]
        self.clientSockets=[]
        self.clientAddrs=[]
        self.clientIDs=[]
        self.messageQueue = MessageQueue()

        self.threads=[]
        


    def startThreads(self):
        for _ in range(0,cfg.numThreads):
            t = threading.Thread(target = self.threadWork)
            t.daemon = True
            t.start()
            self.threads.append(t)

    def threadWork(self):
        #queue and switch is so threads get assigned their proper jobs
        job = cfg.jobQueue.get()

        if job == "connections":
            self.awaitConnections()
            
        if job == "recieve":
            self.recieving()
        
        if job == "relay":
            self.relay()


    def awaitConnections(self):
        while self.running:
            clientSocket, addr = self.s.accept()
            clientSocket.settimeout(cfg.waitTime)
            clientUsername = recieve(clientSocket)

            self.clientUsernames.append(clientUsername)
            self.clientSockets.append(clientSocket)
            self.clientAddrs.append(addr)
            self.clientIDs.append(self.nextClientID)
            self.nextClientID+=1

            self.messageQueue.put(f"{clientUsername} Joined The Server")

        
    def recieving(self):
        while self.running:
            for i,sock in enumerate(self.clientSockets):
                try:
                    message = recieve(sock)
                    self.messageQueue.put(f"{self.clientUsernames[i]}> {message}",self.clientIDs[i])
                except:
                    pass

    def relay(self):
        while self.running:
            if not self.messageQueue.empty():
                message,messangerID = self.messageQueue.get()
                print(message)
                for i,sock in enumerate(self.clientSockets):
                    try:
                        if self.clientIDs[i]!= messangerID:
                            send(sock,message)
                    except:
                        self.dropUser(i)
    
    def dropUser(self,i):
        self.messageQueue.put(f"{self.clientUsernames[i]} Disconnected")
        self.clientSockets[i].close()
        del self.clientUsernames[i]
        del self.clientAddrs[i]
        del self.clientSockets[i]
        del self.clientIDs[i]

    def closeSockets(self):
        for sock in self.clientSockets:
            sock.close()
        
        self.clientUsernames.clear()
        self.clientAddrs.clear()
        self.clientSockets.clear()
        self.clientIDs.clear()

if __name__ == "__main__":
    serv=Server()
    serv.startThreads()
    while True:
        sleep(10)

    serv.closeSockets()