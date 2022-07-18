import socket

class Client:
    #initialize the client class
    def __init__(self):
        self.HEADER = 64
        self.PORT = 5080
        self.SERVER = '127.0.0.1'
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = '!DISCONNECT'
        self.ADDR = (self.SERVER, self.PORT)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)

    #send message to the server
    def send_msg(self, msg):
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
    
    #Run the client side
    def run(self, scorer, score):
        msg = input('Enter team and score: ')
        self.send_msg(msg)     


if __name__ == "__main__":
    app = Client()
    app.run('Graham', '0738445022Gm')
