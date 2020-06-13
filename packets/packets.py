from enum import Enum,auto
from queue import Queue
import pickle


class PType(Enum):
    eot=auto()                    #eot flag, data contains optional message
    message=auto()                #data contains userID of sender and message
    clientData=auto()             #tup of data client data in dictionary
    clientDisconnect=auto()       #id of client disconnected
    ping=auto()                   #data is empty

def sendPacket(sock,pType,data):
    packet=pickle.dumps((pType,data))
    try:
        sock.send(packet)
        return True
    except:
        return False


def getPacket(sock,bufferSize):
    packet = sock.recv(bufferSize)
    pType,data = pickle.loads(packet)

    return pType,data

# enforces formatting
def makeClientDataDict(clientId,username,color):
    return {"id":clientId, "username":username, "color":color}


class SendQueue:
    def __init__(self):
        self.packet = Queue()
        self.console = Queue()
    
    def addEot(self):
        self.packet.put((PType.eot,""))
        self.console.put("")

    def addMessage(self,message,clientId=-1,username=""):
        self.packet.put((PType.message,(clientId,message)))
        self.console.put(f"{username}> {message}")

    def addClientData(self,clientDict):
        self.packet.put((PType.clientData,(clientDict,)))

        username = clientDict["username"]
        self.console.put(f"Sending {username}'s Data")
    
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