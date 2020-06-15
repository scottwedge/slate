import socket
from time import sleep

from packets.packets import PType,sockWrapper
from server.helpers import startServer, getRoomName
from server.structures import ClientData
import server.threads as threads
import server.config as cfg


class Server:
    def __init__(self):
        self.nextClientID = 0
        self.running = True

        self.roomName = getRoomName()
        self.s = startServer()

        self.clients = []

        self.threads=[]

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

            for client in self.clients:
                client.sock.addClientData(newClient.dict)
                client.sock.addMessage(message)
                
            client.sock.sock.settimeout(cfg.waitTime)
            self.nextClientID+=1
            
    #if 2 users have the same username, one joining is given a suffix
    def ensureUniqueUsername(self,username):
        if username == "":
            username = cfg.noNameReplacement

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
            print("recieved EOT")
            self.dropClient(client)

        elif pType == PType.message:
            messangerID, message = data
            username = client.dict["username"]
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
                        consoleMessage = client.sock.send()
                        client.lock.release()
                        print(consoleMessage)

                    #client not recieving packets
                    except:
                        client.lock.release()
                        self.dropClient(client)


    def dropClient(self,client):
        username=client.dict["username"]
        print(f"Dropping {username}")
        clientId = client.dict["id"]
        self.clients.remove(client)
        for client in self.clients:
            client.sock.addClientDisconnect(clientId,username)