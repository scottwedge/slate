import threading

def startThreads(client):
    jobs = client.threadJobs

    retrieveTread = threading.Thread(target = client.recievingLoop)
    retrieveTread.daemon = True
    retrieveTread.start()
    client.threads[jobs[0]] = retrieveTread