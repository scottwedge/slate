import sqlite3
import os
from queue import Queue
from time import time
from datetime import datetime

import server.config as cfg



class MessageDB:
    def __init__(self):
        self.operationsQueue=Queue()

        self.generateChatLogStr ='''
            CREATE TABLE IF NOT EXISTS chatLog (
            messageID integer PRIMARY KEY, 
            time integer NOT NULL, 
            username text NOT NULL, 
            clientID integer NOT NULL, 
            message text NOT NULL
            );'''

        self.putStr = '''
            INSERT INTO chatLog
            (time,username,clientID,message)
            VALUES(?,?,?,?);'''
        
        self.numMessagesStr = "SELECT Count(*) FROM chatLog;"
        
        self.getNStr = '''
            SELECT * FROM chatLog 
            ORDER BY messageID DESC
            Limit ?; '''

        #deletion strings
        self.delAllRows="DELETE FROM chatLog"
        self.delOldestStr = '''
            DELETE FROM chatLog
            WHERE messageID = (SELECT min(messageID) FROM chatLog); '''

        self.delUsernameStr = '''
            DELETE FROM chatLog
            WHERE username = ?; '''
        
        self.delclientIDStr = '''
            DELETE FROM chatLog
            WHERE clientID = ?; '''
        
        self.delMessageID='''
            DELETE FROM chatLog
            WHERE messageID = ?; '''

        self.generate()

    #used as an interface for threads trying to add to the queue
    def addToQueue(self,operation,args):
        self.operationsQueue.put((operation,args))
    def pushQueue(self):
        while not self.operationsQueue.empty():
            operation, args = self.operationsQueue.get()
            operation(*args)

    def generate(self):
        self.conn = sqlite3.connect(cfg.dbPath)
        db = self.conn.cursor()

        db.execute(self.generateChatLogStr)
        self.db = db
        

    def clear(self):
        with self.conn:
            self.db.execute(self.delAllRows)

        
    def put(self,username,clientID,message):
        currentTime = round(time())
        with self.conn:
            self.db.execute(self.putStr,(currentTime,username,clientID,message))
        
    
    def num(self):
        with self.conn:
            self.db.execute(self.numMessagesStr)
            n = self.db.fetchall()[0][0]
        
        return n

    def getN(self,n):
        try:
            n=int(n)

        except:
            print(f"{n} Cannont be Interpreted as an Int\n")
            return []
        
        self.db.execute(self.getNStr,(str(n),))
        messages = self.db.fetchall()

        for i,message in enumerate(messages):
            dateTime=datetime.fromtimestamp(message[1])
            messages[i] = f"MsgID: {message[0]}: {dateTime}: {message[2]}(ID:{message[3]})> {message[4]}"
        
        messages.reverse()
        return messages

    def delOldestN(self,n):
        try:
            n=int(n)

        except:
            print(f"{n} Cannont be Interpreted as an Int\n")
            return 

        with self.conn:
            for _ in range(n):
                self.db.execute(self.delOldestStr)
        
    
    def delByUsername(self,username):
        with self.conn:
            self.db.execute(self.delUsernameStr,(username,))
        
    
    def delByClientID(self,clientID):
        try:
            clientID=int(clientID)

        except:
            print(f"{clientID} Cannont be Interpreted as an Int\n")
            return 

        with self.conn:
            self.db.execute(self.delclientIDStr,str(clientID))
        