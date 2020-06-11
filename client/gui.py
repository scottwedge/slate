import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import config as cfg

class Gui:
    def __init__(self,enterCallback):
        self.tkRoot = tk.Tk()
        self.tkRoot.title(cfg.windowName)
        self.generateTkinterObjs(enterCallback)
        self.makeLayout()

        self.lastMessanger=""

    def generateTkinterObjs(self,enterCallback):
        self.tkRoot.geometry(cfg.tkinterWinSize)
        self.tkRoot.option_add( "*font", cfg.tkinterFont)
        window=tk.Frame(self.tkRoot)
        window.pack(fill='both',expand=True)
        window.configure(background= cfg.softBlack)


        #root note selection
        messages=scrolledtext.ScrolledText(window)
        messages.configure(background= cfg.darkGrey,foreground="white",borderwidth=0,padx=10)

        textVar=tk.StringVar(window)
        textInput=tk.Entry(window,textvariable=textVar)
        textInput.configure(background= cfg.grey,foreground="white",borderwidth=cfg.textInputPad,relief=tk.FLAT)
        #binds return key to sumbit text
        textInput.bind("<Return>", lambda event: enterCallback(textVar) )

        usersActive=tk.Text(window)
        usersActive.configure(background=cfg.softBlack, foreground = "white",borderwidth=0,padx=10,pady=5)
        #to become submit button
        #generateButton=tk.Button(window,text="Generate",command=lambda: eventHand.generateButton(app,cfg,plotter,getTuningList(tuningStrVar),root.get(),scale.get()))
        #generateButton.configure(background= 'red',activebackground='#404040')

    
        self.window=window
        self.messages=messages
        self.textInput = textInput
        self.usersActive=usersActive
    
    def makeLayout(self):

        self.messages.grid(row=0,sticky = tk.NSEW)

        self.textInput.grid(row=1,sticky = 'sew')
        self.usersActive.grid(row=0, column=1,sticky='nes',rowspan=2)

        self.window.rowconfigure(0,weight=2)
        #self.window.rowconfigure(1,weight=1)
        self.window.columnconfigure(0,weight=1)
        self.window.columnconfigure(1,weight=3)
    
    #formats based on whos speaking
    def addMessage(self,message,username):
        if username == self.lastMessanger:
            self.messages.insert(tk.END,message+"\n")
        
        else:
            self.lastMessanger = username
            self.messages.insert(tk.END,f"\n{username}> {message}\n")
        
        self.messages.see(tk.END)


    #username is simply for api compatibility
    def addText(self,text,username=""):
        self.lastMessanger=username
        self.messages.insert(tk.END,f"\n{text}\n")

        self.messages.see(tk.END)


    def updateUsers(self,users):
        self.updateUserList=False
        self.usersActive.delete(1.0,tk.END)
        for user in users:
            self.usersActive.insert(tk.END,user+"\n")
