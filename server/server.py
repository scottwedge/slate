import socket

from packets.packets import PType,getPacket,sendPacket,SendQueue
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


        self.toSend = SendQueue()

        self.clients = []

        self.threads=[]

        threads.startThreads(self)

    def getClientById(self,clientId):
        for client in self.clients:
            if client.dict["id"]==clientId:
                return client
        
        return None

    def awaitConnections(self):
        while self.running:
            try:
                clientSocket, addr = self.s.accept()

                #gets userdata
                _,data = getPacket(clientSocket,cfg.bufferSize)
                clientDataDict = data[0]

                clientUsername = clientDataDict["username"]
                clientUsername=self.ensureUniqueUsername(clientUsername)
            except:
                continue
            #updates client data dict with proper user id
            clientDataDict["id"]=self.nextClientID
            clientDataDict["username"]=clientUsername
            sendPacket(clientSocket,PType.clientData,(clientDataDict,))

            #sends active users
            clientDicts=[]
            for client in self.clients:
                clientDicts.append(client.packageData())
            sendPacket(clientSocket,PType.clientData,tuple(clientDicts))
            
            clientSocket.settimeout(cfg.waitTime)
            
            newClient = ClientData(clientSocket,addr,clientDataDict)
            self.clients.append(newClient)

            self.toSend.addClientData(newClient.dict)

            message=f"> {clientUsername} Joined {self.roomName}"
            self.toSend.addMessage(message)

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
            self.dropClient(client)

        elif pType == PType.message:
            messangerID, message = data
            username = client.dict["username"]
            self.toSend.addMessage(message, messangerID,username)

        elif pType == PType.clientData:
            print("ClientData Recieved Unexpectedly")

        elif pType == PType.clientDisconnect:
            print("ClientDisconnect Packet Intended for Server to Client Only")
        
        elif pType == PType.ping:
            pass
        
        else:
            print("Recieved Invalid Packet Type")

    def recieving(self):
        while self.running:
            for client in self.clients:
                try:
                    pType,data = getPacket(client.sock,cfg.bufferSize)
                    self.packetSwitch(pType,data,client)
                except:
                    continue


    def relay(self):
        while self.running:
            if not self.toSend.empty():
                packet,consoleMessage = self.toSend.get()
                pType,data = packet
                print(consoleMessage)
                for client in self.clients:
                    username = client.dict["username"]
                    try:
                        client.lock.acquire()
                        sendPacket(client.sock,pType,data)
                        client.lock.release()
                    
                    #client not recieving packets
                    except:
                        client.lock.release()
                        self.dropClient(client)


    def dropClient(self,client):
        username=client.dict["username"]
        clientId = client.dict["id"]
        self.clients.remove(client)
        self.toSend.addClientDisconnect(clientId,username)

        

    def disconnectAll(self):
        print(f"Closing {self.roomName}")
        for client in self.clients:
            try:
                client.lock.acquire()
                sendPacket(client.sock,PType.message,(-1,f"{self.roomName} has Closed"))
                client.lock.release()
                client.remove(self.clients)
            except:
                client.lock.release()