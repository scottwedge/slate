from queue import Queue
bufferSize = 1024

port=1234

encoding="utf-8"

queueLen=5

waitTime=0



#Threading jobs
jobQueue=Queue()
jobs=["connections","recieve","relay"]
numThreads = len(jobs)

for job in jobs:
    jobQueue.put(job)