import socket
from time import sleep
from enum import Enum
from queues import EventQueue

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

class Client:
    def __init__(self):

        self.state=States.connecting
        self.username = getUsername()

        self.otherUsers=[]

        self.gui = Gui(self.textSubmitted)

        self.threadJobs=["recieve"]
        self.threads={}

        self.eventQueue = EventQueue()

        self.connectToServ()
        threads.startThreads(self)


        
    def connectToServ(self):
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
            sent = sendPacket(sock,False, self.username)

            if not sent:
                sock.close()
                self.state = States.failedToConnect

            #gets other users in chatroom
            _,userChanges,usernames,message=getPacket(sock)
            usernames=usernames.strip().strip(',')

            if usernames:#checks if list is empty
                self.otherUsers.extend(usernames.split(','))

            self.sock = sock
            self.state = States.chatting

        except:
            self.state = States.failedToConnect
    
    
    def disconnect(self):
        self.state = States.closing
        text="Disconnecting from Server"
        self.eventQueue.addEvent(self.gui.addText,(text,))
        sendPacket(self.sock,True,"")
        #waits for server to see leave message
        sleep(1)
        self.sock.close()


    def sendText(self,eot,text):
        sent = sendPacket(self.sock,eot,text)
        if not sent:
            text="Server Disconnected"
            self.eventQueue.addEvent(self.gui.addText,(text,))
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
                eot,userChange,username,message = getPacket(self.sock)

                # checks eot
                if eot:
                    self.state = States.closing
                elif userChange == 0:

                    self.eventQueue.addEvent(self.gui.addMessage,(message,username))

                #packet contains data on users connecting or disconnecting
                else:
                    self.eventQueue.addEvent(self.gui.addText,(message,))
                    usernames=username.split(",")
                    #add users
                    if userChange == 1:
                        self.otherUsers.extend(usernames)
                    #remove users
                    else:
                        for user in usernames:
                            if user in self.otherUsers:
                                self.otherUsers.remove(user)
                            else:
                                print("user not in list")
                    
                    #adds event to update users
                    self.eventQueue.addEvent(self.gui.updateUsers,(self.otherUsers,))


            except:
                if not self.state==States.closing:
                    text="Server Disconnected"
                    self.eventQueue.addEvent(self.gui.addText,(text,))
                    self.state=States.closing




if __name__ == "__main__":
    client=Client()

    while not client.state == States.closing:
        client.guiLoop()
