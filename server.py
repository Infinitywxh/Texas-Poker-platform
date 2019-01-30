from concurrent import futures

import grpc
import time
import random
from lib.texaspoker import State

import communicate.dealer_pb2 as dealer_pb2
import communicate.dealer_pb2_grpc as rpc
from lib.texaspoker import initMoney
from lib.texaspoker import bigBlind
from lib.texaspoker import totalPlayer
from lib.texaspoker import button
class GameServer(rpc.GameServicer):

    def __init__(self):
        # List with all the chat history

        self.request = [[] for col in range(totalPlayer)]
        self.response = [[] for col in range(totalPlayer)]

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
        global initMoney
        global bigBlind
        global totalPlayer
        global button

        state = State(totalPlayer, initMoney, bigBlind)

        # shuffle the cards
        cardHeap = list(range(0, 52))
        random.shuffle(cardHeap)

        # pre-flop begin
        print('$$$ pre-flop begin')

        # small and big blind
        state.nextpos(button)
        state.player[state.currpos].raisebet(bigBlind // 2)
        state.moneypot += bigBlind // 2

        print("## player %s smallBlind: %s" % (state.currpos, bigBlind // 2))
        print(state)
        print(state.player[state.currpos])

        state.nextpos(state.currpos)
        state.player[state.currpos].raisebet(bigBlind)
        state.moneypot += bigBlind

        print(state)
        print(state.player[state.currpos])
        print("## player %s bigBlind: %s" % (state.currpos, bigBlind))

        state.play_round(0, self.request, self.response)

        # pre-flop ended
        state.update(totalPlayer)
        state.sharedcards = cardHeap[0:3]

        # flop begin
        print('$$$ flop begin')

        state.restore(1, button, bigBlind)

        state.play_round(1, self.request, self.response)

        # flop ended
        state.update(totalPlayer)
        state.sharedcards = cardHeap[0:4]

        # turn begin
        print('$$$ turn begin')

        state.restore(2, button, bigBlind)

        state.play_round(2, self.request, self.response)

        # turn ended
        state.update(totalPlayer)
        state.sharedcards = cardHeap[0:5]

        # river begin
        print('$$$ river begin')

        state.restore(3, button, bigBlind)

        state.play_round(3, self.request, self.response)

        # river ended
        state.update(totalPlayer)

        print("game ended")

        # game over, allocate the money pot

        totalmoney = state.moneypot

        while state.playernum > 0:
            pos = state.findwinner()
            t = state.player[pos].totalbet
            sum = 0
            for i in range(totalPlayer):
                sum += min(t, state.player[i].totalbet)
                state.player[i].totalbet -= min(t, state.player[i].totalbet)
                if state.player[i].totalbet == 0:
                    state.player[pos].active = False
                    state.playernum -= 1
            state.player[pos].money += sum

        print('final state:')
        for i in range(totalPlayer):
            print("player %s have money %s" % (i, state.player[i].money))

    @staticmethod
    def void_reply():
        return dealer_pb2.DealerRequest(command='void')



port = 11912
# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
game_server = GameServer()
rpc.add_GameServicer_to_server(game_server, server)
print('Starting server. Listening...', port)
server.add_insecure_port('[::]:' + str(port))
server.start()
# Server starts in background (another thread) so keep waiting
game_server.run()
