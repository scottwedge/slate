import threading
import json

from packets.packets import makeClientDataDict,PType


#holds client data and thread locks
class ClientData:
    def __init__(self,sock,address,clientDict):
        self.lock=threading.Lock()

        self.lock.acquire()
        self.sock=sock

        self.dict = clientDict
        self.lock.release()

    def remove(self,clientList):
        self.lock.acquire()
        clientList.remove(self)
        self.sock.close()
        self.lock.release()
    
    def packageData(self):
        return self.dict


