import threading

def threadWorkSwitch(job,client):
    if job == "recieve":
        return client.recieving

    if job == "send":
        return client.sending

def startThreads(client):
    jobs=["recieve","send"]
    numThreads = len(jobs)

    for i in range(0,numThreads):
        job = jobs[i]
        target =threadWorkSwitch(job,client)

        t = threading.Thread(target = target)
        t.daemon = True
        t.start()
        client.threads.append(t)

