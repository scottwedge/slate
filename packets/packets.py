from enum import Enum,auto
from queue import Queue
from time import sleep
from bitarray import bitarray
import ast

class PType(Enum):
    eot=auto()                    #eot flag, data contains optional message
    message=auto()                #data contains userID of sender and message
    clientData=auto()             #data is tuple of client data
    clientDisconnect=auto()       #id of client disconnected
    ping=auto()                   #data is empty

    iterations = auto()           #data contains number (used in recieving loops)


# enforces formatting
def makeClientDataDict(clientId,username,color):
    return {"id":clientId, "username":username, "color":color}

def clientDictToTup(clientDict):
    return (clientDict["id"], clientDict["username"], clientDict["color"])

def tupToClientDict(tup):
    clientDict={"id":tup[0], "username":tup[1], "color":tup[2]}
    return clientDict


def encodePacket(pType,data):
    if pType == PType.clientData:
        data = clientDictToTup(data)

    packet = str((pType.value,data))
    packet = packet.encode("utf-8")

    return packet


def decodePacket(packet):
    packet = ast.literal_eval(packet)

    pType,data = packet
    pType = PType(pType)

    if pType == PType.clientData:
        data = tupToClientDict(data)
    
    return pType,data
    



class sockWrapper:
    def __init__(self,sock,bufferSize):
        self.sock = sock
        self.bufferSize=bufferSize
        self.inQueue = Queue()

        #console is used for server
        self.outQueue = Queue()
        self.console = Queue()
    
    def clear(self):
        while not self.outEmpty():
            self.outQueue.get()
            self.console.get()
        while not self.inEmpty():
            self.inQueue.get()

    #recieving
    def listen(self):
        stream = self.sock.recv(self.bufferSize)
        stream = stream.decode("utf-8")

        #detects and corrects packet concatination
        stream=stream.split(")(")
        numPackets = len(stream)
        
        if numPackets>1:
            stream[0]+=")"
            self.inQueue.put(stream[0])
            for i in range(1,numPackets-1):
                stream[i] = f"({stream[i]})"
                self.inQueue.put(stream[i])
            stream[-1] = "("+stream[-1]

        self.inQueue.put(stream[-1])
    
    def get(self,blocking = False):
        if blocking:
            while self.inEmpty():
                sleep(0.1)
        pType,data = decodePacket(self.inQueue.get())
        return pType,data

    def inEmpty(self):
        return self.inQueue.empty()


    #sending
    def addEot(self):
        self.outQueue.put((PType.eot,""))
        self.console.put("")

    def addMessage(self,message,clientId=-1,username=""):
        self.outQueue.put((PType.message,(clientId,message)))
        self.console.put(f"relaying {message}")

    def addClientData(self,clientDict):
        self.outQueue.put((PType.clientData,clientDict))

        username = clientDict["username"]
        self.console.put(f"Sending {username}'s Data")
    
    def addClientDisconnect(self,clientId,username):
        self.outQueue.put((PType.clientDisconnect,clientId))
        self.console.put(f"{username} Disconnected")
    
    def addIterations(self,num):
        self.outQueue.put((PType.clientDisconnect,num))
        self.console.put(f"sending iteration num {num}")

    def addGeneric(self,pType,data):
        self.outQueue.put((pType,data))
        self.console.put(f"Sending {pType}")

    def send(self):
        pType,data = self.outQueue.get()
        packet = encodePacket(pType,data)
        self.sock.send(packet)

        return self.console.get()
    
    def outEmpty(self):
        return self.outQueue.empty()


    def close(self):
        self.sock.close()