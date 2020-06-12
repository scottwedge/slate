import socket
from time import sleep
from enum import Enum

from client.queues import EventQueue
from packets.packets import PType, sendPacket, getPacket,getClientDataDict
from client.helpers import connect, getUsername
import client.threads as threads
import client.config as cfg
from client.gui import Gui


class States(Enum):
    connecting=1
    failedToConnect=2

    chatting=3
    closing=4

class Client:
    def __init__(self):

        self.state=States.connecting
        self.username = getUsername()

        #given by server
        self.userID=0

        self.otherUsers=[]
        #sorted by id number
        self.clientsDict = {}

        self.gui = Gui(self.textSubmitted)

        self.threadJobs=["recieve"]
        self.threads={}

        self.eventQueue = EventQueue()

        self.promptToConnect()
        threads.startThreads(self)


        
    def promptToConnect(self):
        self.state=States.connecting
        while self.state == States.connecting:

            self.gui.addText("> What IP Would You Like to Connect to? ")
            self.gui.tkRoot.update()
            
            
            #waits until connection is established in attemptToConnect by textSubmitted callback
            while self.state == States.connecting:
                try:
                    self.gui.tkRoot.update()
                except:
                    #window was closed while awaiting connection input
                    self.state=States.closing
                    break
            
            if self.state == States.failedToConnect:
                self.gui.addText("> Failed to Connect to That IP ")
                self.gui.tkRoot.update()
                self.state = States.connecting
    
    def attemptToConnect(self,ip):
        try:
            sock = connect(ip)
        except:
            self.state = States.failedToConnect
            return
        
        #sends clientData
        dataDict = getClientDataDict(0,self.username)
        sent = sendPacket(sock,PType.clientData,(dataDict,))
        if not sent:
            sock.close()
            self.state = States.failedToConnect

        #gets own user data (for id)
        packet = getPacket(sock,cfg.bufferSize)
        _,clientData = packet
        clientData=clientData[0] #remember clientData is sent in recieved in tup
        self.id = clientData["id"]

        #gets other users in chatroom
        pType,data = getPacket(sock,cfg.bufferSize)
        self.packetSwitch(pType,data)

        self.sock = sock
        self.state = States.chatting
    
    def packetSwitch(self,pType,data):

        if pType == PType.eot:
            self.state=States.closing

        elif pType == PType.message:
            userId,message=data
            if userId !=-1:
                username=self.clientsDict[userId]["username"]
                self.eventQueue.addEvent(self.gui.addMessage,(message,username))
            else:
                self.eventQueue.addEvent(self.gui.addMessage,(message,""))

        elif pType == PType.clientData:
            for clientData in data:
                self.clientsDict[clientData["id"]] = clientData
                self.eventQueue.addEvent(self.gui.updateClientsPanel,(self.clientsDict,))



        elif pType == PType.clientDisconnect:
            username = self.clientsDict[data]["username"]
            self.clientsDict.pop(data,None)
            text = f"{username} Disconnected"
            self.eventQueue.addEvent(self.gui.addText, (text,))
            self.eventQueue.addEvent(self.gui.updateClientsPanel,(self.clientsDict,))

        
        elif pType == PType.ping:
            pass
        
        else:
            print("Recieved Invalid Packet Type")


    def disconnect(self):
        self.state = States.closing
        text="Disconnecting from Server"
        self.eventQueue.addEvent(self.gui.addText,(text,))
        
        sendPacket(self.sock,PType.eot,"")
        #waits for server to see leave message
        sleep(1)
        self.sock.close()

    def serverDisconnected(self):
        if not self.state==States.closing:
            text="Server Disconnected"
            self.eventQueue.addEvent(self.gui.addText,(text,))
            self.state=States.closing

    #callback when enter is hit in text field
    def textSubmitted(self,strVar):
        text=strVar.get()
        strVar.set("")

        #if in connecting phase
        if self.state == States.connecting:
            self.attemptToConnect(text)

        else:
            sendPacket(self.sock,PType.message,(self.id,text))


    #run by main thread
    def guiLoop(self):
        while not self.state == States.closing:
            
            try:
                while not self.eventQueue.empty():
                    self.eventQueue.triggerEvent()

                self.gui.tkRoot.update()
            except:
                self.state = States.closing

        self.disconnect()

    #run by thread
    def recievingLoop(self):
        while not self.state == States.closing:
            pType,data = getPacket(self.sock,cfg.bufferSize)

            self.packetSwitch(pType,data)



            #except:self.serverDisconnected()
