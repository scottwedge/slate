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
            try:
                clientSocket, addr = self.s.accept()

                #gets username
                _,clientUsername = getPacket(clientSocket)
            except:
                continue


            #sends active usernames
            usernames=""
            for client in self.clients:
                usernames+=f"{client.username},"
            sendPacket(clientSocket,False,1,usernames,"")
            
            clientSocket.settimeout(cfg.waitTime)
            clientUsername=self.ensureUniqueUsername(clientUsername)
            self.clients.append(ClientData(clientSocket,addr,clientUsername,self.nextClientID))
            self.nextClientID+=1

            self.messageQueue.put(f"{clientUsername} Joined {self.roomName}",clientUsername,1)

    #if 2 users have the same username, one joining is given a suffix
    def ensureUniqueUsername(self,username):
        if username == "":
            username = cfg.noNameReplacement

        suffix=""
        i=0

        while i < len(self.clients):
            clientName = self.clients[i].username
            if username+str(suffix) == clientName:
                if suffix=="":
                    suffix=1
                else:
                    suffix+=1
                
                i=0
            else:
                i+=1

        return username+str(suffix)


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
                userChanges,username,message = self.messageQueue.get()
                print(f"{username}> {message}")
                for client in self.clients:
                    try:
                        client.lock.acquire()
                        sendPacket(client.sock,False,userChanges,username,message)
                        client.lock.release()
                    
                    #client not recieving packets
                    except:
                        client.lock.release()
                        self.dropClient(client)


    def dropClient(self,client):
        username=client.username
        self.messageQueue.put(f"{username} Disconnected", username, 2)
        self.clients.remove(client)
        

    def disconnectAll(self):
        print(f"Closing {self.roomName}")
        for client in self.clients:
            try:
                client.lock.acquire()
                sendPacket(client.sock,True,0,"",f"{self.roomName} has Closed")
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