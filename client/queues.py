from queue import Queue

#largely for gui events because they cannot be run on threads (tkinter restriction)
class EventQueue:
    def __init__(self):
        self.queue = Queue()

    #data must be in form of tup
    def addEvent(self,callback,data):
        self.queue.put((callback,data))
    
    def triggerEvent(self):
        tup = self.queue.get()
        #unpacks data (tup[1]) as arguments

        tup[0](*tup[1])

    
    def empty(self):
        return self.queue.empty()
    
    def clear(self):
        while not self.empty():
            _ = self.queue.get()