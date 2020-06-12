from time import sleep

from server.server import Server

if __name__ == "__main__":
    serv=Server()
    while serv.running:
        sleep(10)

    serv.disconnectAll()