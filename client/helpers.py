import socket
import json
import client.config as cfg
from packets.packets import makeClientDataDict

def getSaved(gui):
    try:
        file = open(cfg.userJsonPath, 'r')
        userDict = json.load(file)

    except:
        file = open(cfg.userJsonPath, 'w')
        username = gui.prompt("Whats Your Name?")


        for i,color in enumerate(cfg.colors):
            gui.addText(f"{i}: {color}",color)
        
        #loops until valid input
        colorIndex = -1
        while not (colorIndex in range(0,len(cfg.colors))):
            colorIndex = gui.prompt("Whats Your Color (Enter Number)")
            try:
                colorIndex = int(colorIndex)
            except:
                continue
        
        color = cfg.colors[colorIndex]

        userDict = makeClientDataDict(0,username,color)
        json.dump(userDict,file)

    return userDict

#-------------------#
#  Socket Wrappers  #
#-------------------#
def connect(ip):
    ip.strip()
    #ipv4 socket using tcp
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #connect to server
    sock.connect((ip, cfg.port))
    sock.settimeout(cfg.waitTime)
    return sock