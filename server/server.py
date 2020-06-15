import socket
from time import sleep

from packets.packets import PType,sockWrapper
from server.helpers import startServer, getRoomName
from server.structures import ClientData
import server.threads as threads
from server.messageDatabase import MessageDB
import server.config as cfg


class Server:
    def __init__(self):
        self.running = True
        self.roomName = getRoomName()
        self.db = MessageDB()
        

        self.clients = []
        self.threads=[]

    def start(self):
        self.running = True
        self.nextClientID = 0
        self.s = startServer()
        threads.startThreads(self)

    def getClientById(self,clientId):
        for client in self.clients:
            if client.dict["id"]==clientId:
                return client
        
        return None

    #run on thread
    def awaitConnections(self):
        while self.running:
            sleep(cfg.sleepTime)
            try:
                clientSocket, addr = self.s.accept()
            except:
                continue

            
            sockWrap = sockWrapper(clientSocket,cfg.bufferSize)

            #gets userdata
            sockWrap.listen()
            _,clientDataDict = sockWrap.get()

            clientUsername = clientDataDict["username"]
            clientUsername=self.ensureUniqueUsername(clientUsername)

            #updates client data dict with proper user id
            clientDataDict["id"]=self.nextClientID
            clientDataDict["username"]=clientUsername

            sockWrap.addClientData(clientDataDict)
            sockWrap.send()
            
            sockWrap.addIterations(len(self.clients))
            sockWrap.send()

            #sends active users
            for client in self.clients:
                sockWrap.addClientData(client.dict)
                sockWrap.send()
            
            
            newClient = ClientData(sockWrap,addr,clientDataDict)
            self.clients.append(newClient)
            message = f"> {clientUsername} Joined {self.roomName}"

            self.db.addToQueue(self.db.put,("Server",-1,message))
            
            for client in self.clients:
                client.sock.addClientData(newClient.dict)
                client.sock.addMessage(message)
                
            client.sock.sock.settimeout(cfg.waitTime)
            self.nextClientID+=1
            
    #if 2 users have the same username, one joining is given a suffix
    def ensureUniqueUsername(self,username):
        #prevent no name
        if username == "":
            username = cfg.noNameReplacement

        #prevent server name
        elif username == self.roomName:
            suffix = 1

        #prevent duplicate name
        else:
            suffix=""
        i=0
        while i < len(self.clients):
            clientName = self.clients[i].dict["username"]
            if username+str(suffix) == clientName:
                if suffix=="":
                    suffix=1
                else:
                    suffix+=1

                i=0
            else:
                i+=1

        return username+str(suffix)

    #client index is for eot transmission so this method knows who disconnected
    def packetSwitch(self,pType,data,client=None):
        if pType == PType.eot:
            self.dropClient(client)

        elif pType == PType.message:
            messangerID, message = data
            username = client.dict["username"]
            self.db.addToQueue(self.db.put,(username,messangerID,message))
            for client in self.clients:
                client.sock.addMessage(message, messangerID,username)
                

        elif pType == PType.clientData:
            print("ClientData Recieved Unexpectedly")

        elif pType == PType.clientDisconnect:
            print("ClientDisconnect Packet Intended for Server to Client Only")
        
        elif pType == PType.ping:
            pass
        
        else:
            print("Recieved Invalid Packet Type")

    #run on thread
    def recieving(self):
        while self.running:
            sleep(cfg.sleepTime)
            for client in self.clients:
                try:
                    client.sock.listen()
                    pType,data = client.sock.get()
                    self.packetSwitch(pType,data,client)
                except:
                    continue

    #run on thread
    def relay(self):
        while self.running:
            sleep(cfg.sleepTime)
            for client in self.clients:
                while not client.sock.outEmpty() and client in self.clients:
                    try:
                        client.lock.acquire()
                        client.sock.send()
                        client.lock.release()

                    #client not recieving packets
                    except:
                        client.lock.release()
                        self.dropClient(client)


    def dropClient(self,client):
        username=client.dict["username"]
        self.db.addToQueue(self.db.put,("Server",-1,f"{username} Disconnected"))

        clientId = client.dict["id"]
        client.sock.close()
        self.clients.remove(client)
        for otherClients in self.clients:
            otherClients.sock.addClientDisconnect(clientId,username)
    
    def close(self):
        if self.running:
            print("Closing...")
            self.db.addToQueue(self.db.put,("Server",-1,f"Closing"))

            #sends client eot
            for client in self.clients:
                client.lock.acquire()
                client.sock.addEot()
                while not client.sock.outEmpty():
                    try:
                        client.sock.send()
                    except:
                        break
                client.lock.release()

            #closes socket and removes client
            for client in self.clients:
                self.dropClient(client)

            self.running = False

            self.threads.clear()
            self.clients.clear()
            self.s.close()
            print("Server Closed\n")

        else:
            print("Server Not Started\n")