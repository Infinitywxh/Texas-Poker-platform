from concurrent import futures

import grpc
import time

import communicate.dealer_pb2 as dealer_pb2
import communicate.dealer_pb2_grpc as rpc
import main

class GameServer(rpc.GameServicer):

    def __init__(self):
        # List with all the chat history

        self.request = [[] for col in range(state.playernum)]
        self.response = [[] for col in range(state.playernum)]

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
        # print('gamestream called')
        # while True:
            # print('a loop in server')
            # Check if there are any new messages
        for item in request_iterator:
            # print('server received a requeset')
            if item.type == 1:
                self.request.append(item)
            while len(self.response) != 0:
                yield self.response.pop()

    def run(self):
        main.mainroutine()

    @staticmethod
    def void_reply():
        return dealer_pb2.DealerRequest(command='void')


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
