from concurrent import futures

import grpc
import time

import communicate.dealer_pb2 as dealer_pb2
import communicate.dealer_pb2_grpc as rpc


class GameServer(rpc.GameServicer):

    def __init__(self, state):
        # List with all the chat history
        self.state = state

        self.request = []
        self.response = []

    # The stream which will be used to send new messages to clients
    def GameStream(self, request_iterator, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages

        :param request_iterator:
        :param context:
        :return:
        """
        lastindex = 0
        # For every client a infinite loop starts (in gRPC's own managed thread)
        while True:
            # Check if there are any new messages
            for item in request_iterator:
                self.request.append(item)
                while len(self.response) != 0:
                    yield self.response.pop()

    def run(self):
        while True:
            if len(self.request) != 0:
                request = self.request.pop()
                self.response.append(GameServer.void_reply())
            time.sleep(0.1)

    @staticmethod
    def void_reply():
        return dealer_pb2.DealerReply(message='void')


if __name__ == '__main__':
    port = 11912
    # create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    game_server = GameServer(None)
    rpc.add_GameServicer_to_server(game_server, server)

    print('Starting server. Listening...', port)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    # Server starts in background (another thread) so keep waiting
    game_server.run()
