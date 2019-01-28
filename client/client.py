import threading

import grpc
import communicate.dealer_pb2 as dealer
import communicate.dealer_pb2_grpc as rpc

address = 'localhost'
port = 11912


class Client(object):

    def __init__(self, u: str):
        # the frame to put ui components on
        self.username = u
        # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.GameStub(channel)

    def send_message(self, event):
        """
        This method is called when user enters something into the textbox
        """
        message = self.entry_message.get()
        if message is not '':
            n = dealer.Note()
            n.name = self.username
            n.message = message
            print("S[{}] {}".format(n.name, n.message))
            self.conn.SendNote(n)


if __name__ == '__main__':
    username = 'bfan'
    c = Client(username)
