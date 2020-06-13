import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import client.config as cfg

class Gui:
    def __init__(self,enterCallback):
        self.tkRoot = tk.Tk()
        self.tkRoot.title(cfg.windowName)
        self.generateTkinterObjs()
        self.makeLayout()

        self.lastMessanger=""
        self.prompting=False
        self.promptReturn=""
        #called in textSubmitted
        self.sendToClient = enterCallback

    def generateTkinterObjs(self):
        self.tkRoot.geometry(cfg.tkinterWinSize)
        self.tkRoot.option_add( "*font", cfg.tkinterFont)
        window=tk.Frame(self.tkRoot)
        window.pack(fill='both',expand=True)
        window.configure(background= cfg.softBlack)


        #main chatbox
        messages=scrolledtext.ScrolledText(window)
        messages.configure(background= cfg.darkGrey,foreground=cfg.defaultTextColor,borderwidth=0,padx=10)

        textVar=tk.StringVar(window)
        textInput=tk.Entry(window,textvariable=textVar)
        textInput.configure(background= cfg.grey,foreground=cfg.defaultTextColor,borderwidth=cfg.textInputPad,relief=tk.FLAT)
        #binds return key to textEntered
        textInput.bind("<Return>", lambda event: self.textEntered(textVar) )

        #clients online panel
        clientsPanel=tk.Text(window)
        clientsPanel.configure(background=cfg.softBlack, foreground = cfg.defaultTextColor,borderwidth=0,padx=10,pady=5)

        #configure color tags
        for color in cfg.colors:
            messages.tag_config(color, foreground=color)
            clientsPanel.tag_config(color, foreground=color)
    
        self.window=window
        self.messages=messages
        self.textInput = textInput
        self.clientsPanel=clientsPanel
    
    def makeLayout(self):

        self.messages.grid(row=0,sticky = tk.NSEW)

        self.textInput.grid(row=1,sticky = 'sew')
        self.clientsPanel.grid(row=0, column=1,sticky='nes',rowspan=2)

        self.window.rowconfigure(0,weight=2)
        #self.window.rowconfigure(1,weight=1)
        self.window.columnconfigure(0,weight=1)
        self.window.columnconfigure(1,weight=3)
    
    #formats based on whos speaking
    def addMessage(self,message,clientDict):
        username = clientDict["username"]
        color = clientDict["color"]
        clientId = clientDict["id"]

        if clientId == self.lastMessanger:
            self.messages.insert(tk.END,message+"\n")
        
        else:
            self.lastMessanger = clientId
            self.messages.insert(tk.END,f"\n{username}", color)
            self.messages.insert(tk.END,f"> {message}\n")
        
        self.messages.see(tk.END)


    #username is simply for api compatibility
    def addText(self,text,color=cfg.defaultTextColor):
        self.lastMessanger=-1
        self.messages.insert(tk.END,f"\n{text}\n", color)

        self.messages.see(tk.END)


    def updateClientsPanel(self,clientsDict):
        self.clientsPanel.delete(1.0,tk.END)
        
        for client in clientsDict.values():
            username = client["username"]
            color = client["color"]
            self.clientsPanel.insert(tk.END,username+"\n", color)

    def textEntered(self,strVar):
        text=strVar.get()
        strVar.set("")

        #puts text into prompt return and 
        #signals to prompt method that prompt was
        #submitted
        if self.prompting:
            self.promptReturn=text
            self.prompting = False

        else:
            self.sendToClient(text)


    def prompt(self,text,color=cfg.defaultTextColor):
        self.addText(text,color)
        self.prompting = True

        while self.prompting:
            self.tkRoot.update()
        
        #textEntered has placed the input into self.promptReturn
        return self.promptReturn
