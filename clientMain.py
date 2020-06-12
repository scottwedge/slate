from client.client import Client,States
if __name__ == "__main__":
    client=Client()

    while not client.state == States.closing:
        client.guiLoop()