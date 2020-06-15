import threading


def threadWorkSwitch(job,server):
    if job == "connections":
        return server.awaitConnections

    if job == "recieve":
        return server.recieving

    if job == "relay":
        return server.relay

def startThreads(server):
    jobs=["connections","recieve","relay"]
    numThreads = len(jobs)

    for i in range(0,numThreads):
        job = jobs[i]
        target =threadWorkSwitch(job,server)

        t = threading.Thread(target = target)
        t.daemon = True
        t.start()
        server.threads.append(t)

