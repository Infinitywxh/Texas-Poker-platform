import sys
VERSION=''
with open('/inc/version.inc') as f:
    lines = f.readlines()
    VERSION = lines[0].split('=')[1].strip()
sys.path.append('/opt/version/'+VERSION+'/python-libs')
import threading
import grpc
import sys
from  pathlib import Path
_current_root = str(Path(__file__).resolve().parents[1])
sys.path.append(_current_root)
import communicate.dealer_pb2 as dealer_pb2
import communicate.dealer_pb2_grpc as rpc
from ubiqtool.thread_jobs import Job
import time
# **************************************modify here to use your own AI! ***************************
from AI.v1_1 import v1_ai
# *************************************************************************************************
from lib.texaspoker import State
from lib.texaspoker import Player

# **************************************modify here to set address and port ***********************
address = 'localhost'
port = 15000
# *************************************************************************************************

key = 'NULL'
step = -1
initMoney = -1
bigBlind = -1
totalPlayer = -1
button = -1
state = State(totalPlayer, initMoney, bigBlind, button)

class Client(object):
    def __init__(self, u: str, AI):
        self.username = u
        # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.GameStub(channel)
        self.ai = AI
        self._lock = threading.Lock()
        self._decision_so_far = []  # history of the decision info from the server
        self._new_response = []     # response list from the server
        self._new_request = []      # request list waiting to send to the server

    def chat_with_server(self):
        while True:
            if len(self._new_request) != 0:
                # yield a resquest from the request list to the server
                msg = self._new_request.pop(0)
                yield msg

    def run(self):
        while True:
            # every 1 sec append a request to the list
            self.add_request(Client.HeartBeat())
            time.sleep(1)

    def start(self):
        global mypos
        global state
        global key
        global step
        global initMoney
        global bigBlind
        global totalPlayer
        global button

        responses = self.conn.GameStream(self.chat_with_server())
        for res in responses:
            self._new_response.append(res)
            if res.type == 2:
                # server asking for a decision from the client
                state.currpos = res.pos
                if res.pos == mypos:
                    decision = self.ai(mypos, state)
                    print('$$$ client made a decision:')
                    print(decision)
                    self.add_request(dealer_pb2.DealerRequest(giveup=decision.giveup,
                    allin=decision.allin, check=decision.check, raisebet=decision.raisebet,
                    callbet=decision.callbet, amount=decision.amount, pos=mypos, type=1, token=key))

            elif res.type == 1:
                # server sending an info to the client to modify the state
                print('client received a info from the server and modify the state')
                print('$$$ giveup=',res.giveup,', check=',res.check,', allin=',res.allin,', callbet=',res.allin,', raisebet=',res.raisebet,
                           ', amount=', res.amount, ', pos=', res.pos)
                print()
                state.currpos = res.pos
                self._decision_so_far.append(res)
                if res.giveup == 1:
                    state.player[state.currpos].active = False
                    state.playernum -= 1
                elif res.check == 1:
                    pass
                elif res.allin == 1:
                    state.moneypot += state.player[state.currpos].money
                    state.player[state.currpos].allinbet()
                    if state.player[state.currpos].bet > state.minbet:
                        state.last_raised = state.player[state.currpos].bet - state.minbet
                        state.minbet = state.player[state.currpos].bet
                elif res.callbet == 1:
                    delta = state.minbet - state.player[state.currpos].bet
                    state.player[state.currpos].raisebet(delta)
                    state.moneypot += delta

                elif res.raisebet == 1:
                    state.last_raised = res.amount - state.minbet
                    state.minbet = res.amount
                    delta = res.amount - state.player[state.currpos].bet
                    state.player[state.currpos].raisebet(delta)
                    state.moneypot += delta

                else:
                    print('impossible condition')
                    # assert(0)

                step += 1
                self._decision_so_far.append(res)

            elif res.type == 3:
                # server send a state control command
                if res.command == 'restore':
                    if res.pos == 1:
                        state.restore(res.pos, button, bigBlind)
                    else:
                        state.restore(res.pos, button, 0)
                elif res.command == 'update':
                    state.update(totalPlayer)
                elif res.command == 'givecard':
                    state.player[res.pos].cards.append(res.num)
                elif res.command == 'sharedcard':
                    state.sharedcards.append(res.num)

            elif res.type == 4:
                # client initialize
                assert(step == -1)
                s = res.command.split()
                initMoney = int(s[0])
                bigBlind = int(s[1])
                totalPlayer = int(s[2])
                button = int(s[3])
                key = res.token
                step = 0

                state = State(totalPlayer, initMoney, bigBlind, button)
                state.last_raised = bigBlind

                # small and big Blind, modify the state
                state.nextpos(button)
                state.player[state.currpos].raisebet(bigBlind // 2)
                state.moneypot += bigBlind // 2
                state.nextpos(state.currpos)
                state.player[state.currpos].raisebet(bigBlind)
                state.moneypot += bigBlind

                print('******client initialized******')

            elif res.type == 5:
                # game over info
                print('***********game over***************')
                print('sharedcards:', state.sharedcards)
                for x in state.sharedcards:
                    print(printcard(x), end='. ')
                print()
                print('cards:', state.player[mypos].cards)
                for x in state.player[mypos].cards:
                    print(printcard(x), end='. ')
                print('\n')
                return

    def add_request(self, msg):
        self._new_request.append(msg)

    @staticmethod
    def HeartBeat():
        # a empty message, only to find if there is new info from the server
        global mypos
        global key
        global step
        return dealer_pb2.DealerRequest(command='heartbeat', type=0, pos=mypos,
                                        token=key, status=step)

def printcard(num):
    name = ['spade', 'heart', 'diamond', 'club']
    return '%s, %s' %(name[num%4], num//4)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Error: enter the position for the client!')
    mypos = int(sys.argv[1])
    username = 'bfan'
# ************************************ modify the following sentence to use your own AI********************************
    c = Client(username, v1_ai)
# *********************************************************************************************************************
    Job(c).start()
    c.start()
