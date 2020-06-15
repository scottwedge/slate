
from inspect import signature
import sys


class Operation:
    def __init__(self,funct):
        #Callback function which exacutes the operation
        self.funct = funct

        #number of arguments function takes
        self.numArgs = len(signature(funct).parameters)

def printHelp():
    message ='''
Commands:
    exit                -Close Application
    start               -Launch Server
    close               -Close Server
    clients             -Show Connected Clients Data
    messages [n]        -Show most recent n messages
    numMessages         -Shows How Many Messages are in the Database
    delOldest [n]       -delete the oldest n messages
    clear               -delete all messages
    '''
    print(message)

def exitWrapper():
    print("Closing App")
    sys.exit()
    
def loadCommands(server):

    commandsDict = {
        "exit": Operation(exitWrapper),
        "help": Operation(printHelp),
        "start": Operation(server.start),
        "close": Operation(server.close),

        "clients": Operation(lambda: print( "\n".join([str(client.dict) for client in server.clients])+"\n" )),
        "messages": Operation(lambda n: print("\n".join(server.db.getN(n))+"\n")),
        "numMessages": Operation(lambda : print(server.db.num(),"\n")),
        "delOldest": Operation(server.db.delOldestN),
        "clear": Operation(server.db.clear),
    }

    return commandsDict