import socket
from time import sleep
from enum import Enum
from queue import Queue

from helpers import connect, sendPacket, getPacket, getUsername
import threads
import struct
import config as cfg
from gui import Gui

class States(Enum):
    connecting=1
    failedToConnect=2

    chatting=3
    closing=4


class PrintQueue:
    def __init__(self,gui):
        self.printTypes={}
        self.printTypes["text"] = gui.addText
        self.printTypes["message"] = gui.addMessage

        self.queue=Queue()

    #format type, message, optional username for message type printing
    def put(self,printType,text,username=""):
        self.queue.put((printType,text,username))

    #submits next print job
    def push(self):
        printType,text,username = self.queue.get()
        self.printTypes[printType](text,username)
    
    def empty(self):
        return self.queue.empty()

class Client:
    def __init__(self):

        self.state=States.connecting
        self.username = getUsername()
        self.gui = Gui(self.textSubmitted)

        self.threadJobs=["recieve"]
        self.threads={}

        self.printQueue = PrintQueue(self.gui)

        self.connectToServ()
        threads.startThreads(self)


        
    def connectToServ(self):
        self.state=States.connecting
        while self.state == States.connecting:

            self.gui.addText("> What IP Would You Like to Connect to? ")
            self.gui.tkRoot.update()
            
            
            #waits until connection is established in attemptToConnect by textSubmitted callback
            while self.state == States.connecting:
                self.gui.tkRoot.update()
            
            if self.state == States.failedToConnect:
                self.gui.addText("> Failed to Connect to That IP ")
                self.gui.tkRoot.update()
                self.state = States.connecting
    
    def attemptToConnect(self,ip):
        try:
            sock = connect(ip)
            sent = sendPacket(sock,False, self.username)

            if not sent:
                sock.close()
                self.state = States.failedToConnect

            self.sock = sock
            self.state = States.chatting

        except:
            self.state = States.failedToConnect
    
    
    def disconnect(self):
        self.state = States.closing
        self.printQueue.put("text","Disconnecting from Server")
        sendPacket(self.sock,True,"")
        #waits for server to see leave message
        sleep(1)
        self.sock.close()


    def sendText(self,eot,text):
        sent = sendPacket(self.sock,eot,text)
        if not sent:
            self.printQueue.put("text","Server Disconnected")
            self.state=States.closing


    #callback when enter is hit in text field
    def textSubmitted(self,strVar):
        text=strVar.get()
        strVar.set("")

        #detects user attempting disconnect by phrase
        eot=False
        if text == cfg.closePhrase:
            eot=True
            self.state = States.closing

        #if in connecting phase
        if self.state == States.connecting:
            self.attemptToConnect(text)

        else:
            self.sendText(eot,text)


    #run by main thread
    def guiLoop(self):
        while not self.state == States.closing:
            
            try:
                while not self.printQueue.empty():
                    self.printQueue.push()

                self.gui.tkRoot.update()
            except:
                self.state = States.closing

        self.disconnect()

    #run by thread
    def recievingLoop(self):
        while not self.state == States.closing:
            try:
                eot,username,message = getPacket(self.sock)
                # checks eot
                if eot:
                    self.state = States.closing
                else:
                    self.printQueue.put("message",message,username)
            except:
                if not self.state==States.closing:
                    self.printQueue.put("text","Server Disconnected")
                    self.state=States.closing




if __name__ == "__main__":
    client=Client()

    while not client.state == States.closing:
        client.guiLoop()
