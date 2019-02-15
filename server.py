from concurrent import futures

import grpc
import time
from time import sleep
import random
from lib.texaspoker import State

import communicate.dealer_pb2 as dealer_pb2
import communicate.dealer_pb2_grpc as rpc

# *************************************可修改的游戏参数*********************************
initMoney = 1000    # 初始金钱
bigBlind = 20       # 大盲注
totalPlayer = 3     # 玩家人数
button = 0          # 庄家位置

# state为局面
global state
state = State(totalPlayer, initMoney, bigBlind, button)

# generate_Key生成10位随机密钥，用于校验client身份
def generate_Key():
    s = ''
    for i in range(10):
        n = random.randint(97, 122)
        s += chr(n)
    return s

# rpc server
class GameServer(rpc.GameServicer):
    global state
    def __init__(self):
        self.keys = []  # 各client密钥
        self.request = [[] for col in range(totalPlayer)]   # each client's request pending list
        self.response = [[] for col in range(totalPlayer)]  # each client's response pending list
        self._response_so_far = [[] for col in range(totalPlayer)]  # each client's response history
        for i in range(totalPlayer):
            self.keys.append(generate_Key())

    # client端调用的句柄
    def GameStream(self, request_iterator, context):
        global initMoney
        global bigBlind
        global totalPlayer
        global button
        global state
        # Check if there are any new messages
        for item in request_iterator:
            if item.status == -1:
                # handle initialize request from the client, send basic information
                print('*****client %s initialized!********' % item.pos)
                s = str(initMoney)+' '+str(bigBlind)+' '+str(totalPlayer)+' '+str(button)
                tmp = self.response[item.pos]
                self.response[item.pos] = []
                self.response[item.pos].append(dealer_pb2.DealerRequest(type=4,command=s,pos=item.pos,token=self.keys[item.pos]))
                for exp in self._response_so_far[item.pos]:
                    self.response[item.pos].append(exp)
                for exp in tmp:
                    if exp.type == 2:
                        self.response[item.pos].append(exp)

            elif item.token != self.keys[item.pos]:
                print('invalid key!')
                # the secure key is not matched
                yield dealer_pb2.DealerRequest(type=6, command='invalid key')

            elif item.type == 1:
                # a decision from the client, push to the request list
                self.request[item.pos].append(item)

            while len(self.response[item.pos]) != 0:
                # yield a response for the client
                yield self.response[item.pos].pop(0)

    def run(self):
        # server main routine
        global initMoney
        global bigBlind
        global totalPlayer
        global button
        global state

        sleep(2)
        print()
        print('totalPlayer:', totalPlayer, 'bigBlind:', bigBlind, 'initMoney:', initMoney, 'button:', button)
        print('**********game started*************')

        # shuffle the cards
        cardHeap = list(range(0, 52))   # 牌堆
        random.shuffle(cardHeap)
        heappos = 0     # 牌堆指针

        # give each player 2 cards
        for i in range(totalPlayer):
            if state.player[i].active == False:
                continue
            state.player[i].cards.append(cardHeap[heappos])
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='givecard', pos=i, num=cardHeap[heappos])) 
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3,command='givecard',pos=i,num=cardHeap[heappos]))
            heappos += 1
            state.player[i].cards.append(cardHeap[heappos])
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='givecard', pos=i, num=cardHeap[heappos]))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3,command='givecard',pos=i,num=cardHeap[heappos]))
            heappos += 1

        print()

        # pre-flop round begin
        print('$$$ pre-flop begin')
        state.last_raised = bigBlind

        # small and big blind
        state.nextpos(button)
        state.player[state.currpos].raisebet(bigBlind // 2)
        state.moneypot += bigBlind // 2

        print("## player %s smallBlind: %s" % (state.currpos, bigBlind // 2))
        print(state)
        print(state.player[state.currpos])
        print('\n')
        state.nextpos(state.currpos)
        state.player[state.currpos].raisebet(bigBlind)
        state.moneypot += bigBlind

        print("## player %s bigBlind: %s" % (state.currpos, bigBlind))
        print(state)
        print(state.player[state.currpos])
        print('\n')
        for i in range(totalPlayer):
            t = dealer_pb2.DealerRequest(giveup=0,
                            allin=0, check=0, callbet=1,
                            raisebet=0, amount=bigBlind, pos=state.currpos, type=1)
            self.response[i].append(t)
            self._response_so_far[i].append(t)

        state.play_round(0, self.request, self.response, self._response_so_far)

        # pre-flop round ended

        state.update(totalPlayer)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
        # three shared cards
        state.sharedcards.append(cardHeap[heappos])
        state.sharedcards.append(cardHeap[heappos+1])
        state.sharedcards.append(cardHeap[heappos+2])
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[heappos]))
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[heappos+1]))
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[heappos+2]))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[heappos]))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[heappos+1]))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[heappos+2]))
        heappos += 3

        # flop round begin
        print('$$$ flop begin')

        state.restore(1, button, bigBlind)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=1))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=1))
        state.play_round(1, self.request, self.response, self._response_so_far)


        # flop round ended
        state.update(totalPlayer)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
        
        state.sharedcards.append(cardHeap[heappos])
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[heappos]))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[heappos]))
        heappos += 1

        # turn round begin
        print('$$$ turn begin')

        state.restore(2, button, 0)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=2))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=2))

        state.play_round(2, self.request, self.response, self._response_so_far)

        # turn round ended
        state.update(totalPlayer)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='update'))

        state.sharedcards.append(cardHeap[heappos])
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[heappos]))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='sharedcard', num=cardHeap[heappos]))
        heappos += 1

        # river round begin
        print('$$$ river begin')

        state.restore(3, button, 0)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=3))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='restore', pos=3))

        state.play_round(3, self.request, self.response, self._response_so_far)

        # river round ended
        state.update(totalPlayer)
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
            self._response_so_far[i].append(dealer_pb2.DealerRequest(type=3, command='update'))
        print()
        print("*********game ended************")

        # game over, allocate the money pot

        while state.playernum > 0:
            pos = state.findwinner()
            t = state.player[pos].totalbet
            sum = 0
            for i in range(totalPlayer):
                sum += min(t, state.player[i].totalbet)
                state.player[i].totalbet -= min(t, state.player[i].totalbet)
                if state.player[i].totalbet == 0:
                    state.player[i].active = False
                    state.playernum -= 1
            state.player[pos].money += sum


        print('final state:')
        print('shared cards:', state.sharedcards)
        for x in state.sharedcards:
            print(printcard(x), end='. ')
        print('\n\n')
        print('playercards:')
        for i in range(totalPlayer):
            print('player', i, 'cards:', state.player[i].cards)
            for x in state.player[i].cards:
                print(printcard(x), end='. ')
            print('\n\n')
        for i in range(totalPlayer):
            print("player %s have money %s" % (i, state.player[i].money))
        for i in range(totalPlayer):
            self.response[i].append(dealer_pb2.DealerRequest(type=5))


# 按花色点数打印一张牌
def printcard(num):
    name = ['spade', 'heart', 'diamond', 'club']
    return '%s, %s' %(name[num%4], num//4)

if __name__ == '__main__':
    # ************ set the listening port here *****************
    port = 15000
    # create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    game_server = GameServer()
    rpc.add_GameServicer_to_server(game_server, server)
    print('Starting server. Listening...', port)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    # Server starts in background (another thread) so keep waiting
    game_server.run()
