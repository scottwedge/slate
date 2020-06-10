import socket
import keyboard
import threading
from time import sleep
from queue import Queue
from socketWrappers import startServer, send, recieve

import config as cfg


def getRoomName():
    try:
        file = open("roomName.txt", 'r')

        name = file.readline()
        if not name:
            file = open("roomName.txt", 'w')
            name = input("What Would You Like To Name This Chat Room: ")
            file.write(name)

    except IOError:
        file = open("roomName.txt", 'w')
        name = input("What Would You Like To Name This Chat Room: ")
        file.write(name)

    return name

#holds client data and thread locks
class Client:
    def __init__(self,sock,address,username,Id):
        self.lock=threading.Lock()

        self.lock.acquire()
        self.username = username
        self.id = Id
        self.sock=sock
        self.lock.release()

    def remove(self,clientList):
        self.lock.acquire()
        clientList.remove(self)
        self.sock.close()
        self.lock.release()
        return self.username
    


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

        self.roomName = getRoomName()
        self.s = startServer()


        self.messageQueue = MessageQueue()

        self.clients = []
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

            self.clients.append(Client(clientSocket,addr,clientUsername,self.nextClientID))
            self.nextClientID+=1

            self.messageQueue.put(f"{clientUsername} Joined {self.roomName}")

        
    def recieving(self):
        while self.running:
            for client in self.clients:
                try:
                    client.lock.acquire()
                    message = recieve(client.sock)
                    self.messageQueue.put(f"{client.username}> {message}",client.id)
                    client.lock.relase()
                except:
                    client.lock.release()

    def relay(self):
        while self.running:
            if not self.messageQueue.empty():
                message,messangerID = self.messageQueue.get()
                print(message)
                for client in self.clients:
                
                    try:
                        client.lock.acquire()
                        if client.id!= messangerID:
                            send(client.sock,message)
                        
                        client.lock.release()
                    except:
                        client.lock.release()
    
    def dropClient(self,i):
        username = self.clients[i].remove()
        self.messageQueue.put(f"{username} Disconnected")

    def disconnectAll(self):
        print(f"Closing {self.roomName}")
        for client in self.clients:
            try:
                client.lock.acquire()
                send(client.sock,f"{self.roomName} has Closed")
                client.lock.release()
                _ = client.remove()
            except:
                client.lock.release()

if __name__ == "__main__":
    serv=Server()
    serv.startThreads()
    while True:
        sleep(10)

    serv.disconnectAll()