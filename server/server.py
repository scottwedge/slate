import socket
from time import sleep

from helpers import startServer, sendPacket, getPacket, getRoomName
from structures import ClientData,MessageQueue
import threads 
import config as cfg


class Server:
    def __init__(self):
        self.nextClientID = 0
        self.running = True

        self.roomName = getRoomName()
        self.s = startServer()


        self.messageQueue = MessageQueue()

        self.clients = []
        self.threads=[]

    def awaitConnections(self):
        while self.running:
            clientSocket, addr = self.s.accept()
            clientSocket.settimeout(cfg.waitTime)

            #gets username
            _,clientUsername = getPacket(clientSocket)

            self.clients.append(ClientData(clientSocket,addr,clientUsername,self.nextClientID))
            self.nextClientID+=1

            self.messageQueue.put(f"{clientUsername} Joined {self.roomName}")

        
    def recieving(self):
        while self.running:
            for client in self.clients:
                try:
                    client.lock.acquire()
                    eot,message = getPacket(client.sock)
                    #client disconnecting
                    if eot:
                        client.lock.release()
                        self.dropClient(client)
                        continue
                    
                    self.messageQueue.put(message, client.username)
                    client.lock.relase()
                except:
                    client.lock.release()

    def relay(self):
        while self.running:
            if not self.messageQueue.empty():
                username,message = self.messageQueue.get()
                print(f"{username}> {message}")
                for client in self.clients:
                    try:
                        client.lock.acquire()
                        sendPacket(client.sock,False,username,message)
                        client.lock.release()
                    
                    #client not recieving packets
                    except:
                        client.lock.release()
                        self.dropClient(client)


    def dropClient(self,client):
        self.messageQueue.put(f"{client.username} Disconnected")
        self.clients.remove(client)
        

    def disconnectAll(self):
        print(f"Closing {self.roomName}")
        for client in self.clients:
            try:
                client.lock.acquire()
                sendPacket(client.sock,True,"",f"{self.roomName} has Closed")
                client.lock.release()
                client.remove(self.clients)
            except:
                client.lock.release()

if __name__ == "__main__":
    serv=Server()
    threads.startThreads(serv)
    while serv.running:
        sleep(10)

    serv.disconnectAll()