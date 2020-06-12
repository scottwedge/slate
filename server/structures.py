import threading
from queue import Queue
import json

from packets.packets import getClientDataDict,PType
#holds client data and thread locks
class ClientData:
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
    
    def packageData(self):
        self.lock.acquire()

        clientDict = getClientDataDict(self.id,self.username)

        self.lock.release()

        return clientDict


class SendQueue:
    def __init__(self):
        self.packet = Queue()
        self.console = Queue()
    
    def addMessage(self,message,clientId=-1,username=""):
        self.packet.put((PType.message,(clientId,message)))
        self.console.put(f"{username}> {message}")

    def addClientData(self,client):
        self.packet.put((PType.clientData,(client.packageData(),)))
        self.console.put(f"Sending {client.username}'s Data")
    
    def addClientDisconnect(self,clientId,username):
        self.packet.put((PType.clientDisconnect,clientId))
        self.console.put(f"{username} Disconnected")

    def addGeneric(self,pType,data):
        self.packet.put((pType,data))
        self.console.put(f"Sending {pType}")

    
    def get(self):
        return self.packet.get(),self.console.get()
    def empty(self):
        return self.packet.empty()