import socket
from time import sleep
from enum import Enum,auto
import sys
import threading

from client.queues import EventQueue
from packets.packets import PType, sendPacket, getPacket, SendQueue
from client.helpers import connect, getSaved
import client.threads as threads
import client.config as cfg
from client.gui import Gui

class Client:
    def __init__(self):
        self.running = True
        self.gui = Gui(self.textSubmitted,self.close)
        self.dict = getSaved(self.gui)

        #sorted by id number
        self.clientsDict = {}
        self.dictLock = threading.Lock()

        self.threadJobs=["recieve","transmit"]
        self.threads={}

        self.eventQueue = EventQueue()
        self.toSend = SendQueue()

        self.connect()
        threads.startThreads(self)
    
    def connect(self):
        while True:
            ip = self.gui.prompt("> What IP Would You Like to Connect to? ")
            try:
                sock = connect(ip)
            except:
                self.gui.addText("> Failed To Connect To That IP")
                continue

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
            break
    
    def packetSwitch(self,pType,data):
        if pType == PType.eot:
            self.eventQueue.addEvent(self.close,())

        elif pType == PType.message:
            userId,message=data
            if userId !=-1:

                self.dictLock.acquire()
                clientDict=self.clientsDict[userId]
                self.dictLock.release()

                self.eventQueue.addEvent(self.gui.addMessage,(message,clientDict))
            else:
                self.eventQueue.addEvent(self.gui.addText,(message,))

        elif pType == PType.clientData:

            self.dictLock.acquire()
            for clientData in data:
                self.clientsDict[clientData["id"]] = clientData
            self.dictLock.release()

            self.eventQueue.addEvent(self.gui.updateClientsPanel,(self.clientsDict,self.dictLock))

        elif pType == PType.clientDisconnect:

            self.dictLock.acquire()
            username = self.clientsDict[data]["username"]
            self.clientsDict.pop(data,None)
            self.dictLock.release()

            text = f"> {username} Disconnected"
            self.eventQueue.addEvent(self.gui.addText, (text,))
            self.eventQueue.addEvent(self.gui.updateClientsPanel,(self.clientsDict,self.dictLock))

        
        elif pType == PType.ping:
            pass
        
        else:
            print("Recieved Invalid Packet Type")


    def disconnect(self):
        text="Disconnecting from Server"
        self.eventQueue.addEvent(self.gui.addText,(text,))
        
        sendPacket(self.sock,PType.eot,"")

        #waits for server to see leave message
        sleep(1)

        self.sock.close()
    
    def close(self):
        try:# catch for closure before connection
            self.disconnect()
        except:
            pass
        
        #waits for all threads to stop running
        self.running = False
        for job in self.threadJobs:
            if job in self.threads.keys():
                self.threads[job].join()

        sys.exit()

    def serverDisconnected(self):
        text="Server Disconnected"
        self.eventQueue.addEvent(self.gui.addText,(text,))
        self.eventQueue.addEvent(self.close,())

    #callback when enter is hit in text field
    def textSubmitted(self,text):
        self.toSend.addMessage(text,self.dict["id"])

    #run by transmit thread
    def transmit(self):
        while self.running:
            while not self.toSend.empty():
                packet,console = self.toSend.get()
                pType,data = packet
                sendPacket(self.sock,pType,data)
        
    #run by thread
    def recievingLoop(self):
        dropped = 0
        while self.running:
            try:
                pType,data = getPacket(self.sock,cfg.bufferSize)
                self.packetSwitch(pType,data)
                dropped = 0
            except:
                dropped+=1
                if dropped > 5:
                    self.serverDisconnected()

    #run by main thread
    def mainLoop(self):
        while self.running:
            try:
                while not self.eventQueue.empty():
                    self.eventQueue.triggerEvent()

                self.gui.tkRoot.update()
            except:
                break
        self.close()
