import socket
from time import sleep
from enum import Enum,auto
import json

from client.queues import EventQueue
from packets.packets import PType, sendPacket, getPacket,makeClientDataDict, SendQueue
from client.helpers import connect, getUsername
import client.threads as threads
import client.config as cfg
from client.gui import Gui


class States(Enum):
    connecting=auto()
    chatting=auto()
    closing=auto()

class Client:
    def __init__(self):
        self.gui = Gui(self.textSubmitted)
        self.getSaved()

        #sorted by id number
        self.clientsDict = {}

        self.threadJobs=["recieve","transmit"]
        self.threads={}

        self.eventQueue = EventQueue()
        self.toSend = SendQueue()

        self.connect()
        threads.startThreads(self)

    def getSaved(self):
        try:
            file = open("user.json", 'r')
            self.dict = json.load(file)

        except:
            file = open("user.json", 'w')
            username = self.gui.prompt("Whats Your Name?")


            for i,color in enumerate(cfg.colors):
                self.gui.addText(f"{i}: {color}",color)
            
            #loops until valid input
            colorIndex = -1
            while not (colorIndex in range(0,len(cfg.colors))):
                colorIndex = self.gui.prompt("Whats Your Color (Enter Number)")
                try:
                    colorIndex = int(colorIndex)
                except:
                    continue
            
            color = cfg.colors[colorIndex]

            self.dict = makeClientDataDict(0,username,color)
            json.dump(self.dict,file)
    
    def connect(self):
        self.state=States.connecting
        while self.state == States.connecting:
            ip = self.gui.prompt("> What IP Would You Like to Connect to? ")
            ip = ip.strip()
            try:
                sock = connect(ip)
            except:
                self.gui.addText("> Failed To Connect To That IP")
                return

            #sends clientData
            sent = sendPacket(sock,PType.clientData,(self.dict,))
            if not sent:
                sock.close()
                self.gui.addText("> Connected But With No Response")
                continue


            #gets own user data (for id)
            packet = getPacket(sock,cfg.bufferSize)

            _,clientData = packet
            clientData=clientData[0] #remember clientData is sent in recieved in tup
            #allows server to overwrite id and username for runtime
            self.dict = clientData

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
                clientDict=self.clientsDict[userId]
                self.eventQueue.addEvent(self.gui.addMessage,(message,clientDict))
            else:
                self.eventQueue.addEvent(self.gui.addText,(message,))

        elif pType == PType.clientData:
            for clientData in data:
                self.clientsDict[clientData["id"]] = clientData
                self.eventQueue.addEvent(self.gui.updateClientsPanel,(self.clientsDict,))



        elif pType == PType.clientDisconnect:
            username = self.clientsDict[data]["username"]
            self.clientsDict.pop(data,None)
            text = f"> {username} Disconnected"
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
    def textSubmitted(self,text):
        if self.state == States.chatting:
            self.toSend.addMessage(text,self.dict["id"])

    #run by transmit thread
    def transmit(self):
        while not self.state == States.closing:
            while not self.toSend.empty():
                packet,console = self.toSend.get()
                pType,data = packet
                sendPacket(self.sock,pType,data)

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
            try:
                pType,data = getPacket(self.sock,cfg.bufferSize)

                self.packetSwitch(pType,data)

            except:
                self.serverDisconnected()
