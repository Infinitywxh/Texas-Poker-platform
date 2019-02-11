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
global test
test = 0
global state
state = State(totalPlayer, initMoney, bigBlind)
class GameServer(rpc.GameServicer):
    global state
    def __init__(self):
        # List with all the chat history

        self.request = [[] for col in range(totalPlayer)]
        self.response = [[] for col in range(totalPlayer)]
        self._response_so_far = [[] for col in range(totalPlayer)]
    # The stream which will be used to send new messages to clients
    def GameStream(self, request_iterator, context):
        # print('GameServer called')
        # Check if there are any new messages
        for item in request_iterator:
            # print('length of request:', len(self.request[0]), len(self.request[1]), len(self.request[2]))
            # print('itempos:', item.pos)
            if item.type == 1:
                # print('server received a status request from position', item.pos)
                self.request[item.pos].append(item)
                # print('length of request after receive:', len(self.request[0]), len(self.request[1]), len(self.request[2]))
            while len(self.response[item.pos]) != 0:
                # print('server yield a response for position', item.pos)
                yield self.response[item.pos].pop(0)

    def run(self):
        global initMoney
        global bigBlind
        global totalPlayer
        global button
        global state
        

        # shuffle the cards
        cardHeap = list(range(0, 52))
        random.shuffle(cardHeap)

        # pre-flop begin
        print('$$$ pre-flop begin')
        state.last_raised = bigBlind
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

        print("## player %s bigBlind: %s" % (state.currpos, bigBlind))
        print(state)
        print(state.player[state.currpos])
        for i in range(totalPlayer):
            t = dealer_pb2.DealerRequest(giveup=0,
                            allin=0, check=0, callbet=1,
                            raisebet=0, amount=bigBlind, pos=state.currpos, type=1)
            self.response[i].append(t)
            self._response_so_far[i].append(t)

        state.play_round(0, self.request, self.response, self._response_so_far)

        # pre-flop ended
        state.update(totalPlayer)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
        state.sharedcards = cardHeap[0:3]
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[0]))
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[1]))
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[2]))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[0]))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[1]))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[2]))


        heappos = 3
        # flop begin
        print('$$$ flop begin')

        state.restore(1, button, bigBlind)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=1))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=1))
        state.play_round(1, self.request, self.response, self._response_so_far)


        # flop ended
        state.update(totalPlayer)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='update'))

        for i in range(totalPlayer):
            if state.player[i].active == False:
                continue
            state.player[i].cards.append(cardHeap[heappos])
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='givecard', pos=i, num=cardHeap[heappos]))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='givecard', pos=i, num=cardHeap[heappos]))
            heappos += 1


        # turn begin
        print('$$$ turn begin')

        state.restore(2, button, 0)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=2))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=2))

        state.play_round(2, self.request, self.response, self._response_so_far)

        # turn ended
        state.update(totalPlayer)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='update'))

        for x in state.player:
            x.cards.append(cardHeap[heappos])
            heappos += 1
        for i in range(totalPlayer):
            if state.player[i].active == False:
                continue
            state.player[i].cards.append(cardHeap[heappos])
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='givecard', pos=i, num=cardHeap[heappos]))
            heappos += 1


        # river begin
        print('$$$ river begin')

        state.restore(3, button, 0)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=3))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=3))

        state.play_round(3, self.request, self.response, self._response_so_far)

        # river ended
        state.update(totalPlayer)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='update'))

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
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=5))

    @staticmethod
    def void_reply():
        return dealer_pb2.DealerRequest(type=0)


if __name__ == '__main__':
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
