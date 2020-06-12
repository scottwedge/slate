from enum import Enum,auto
import pickle


class PType(Enum):
    eot=auto()                    #eot flag, data contains optional message
    message=auto()                #data contains userID of sender and message
    clientData=auto()             #tup of data client data in dictionary
    clientDisconnect=auto()       #id of client disconnected
    ping=auto()                   #data is empty

#note here to enfoce formatting
def getClientDataDict(clientId,username):
    return {"id": clientId,"username": username}

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