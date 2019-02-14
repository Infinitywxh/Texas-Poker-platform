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
from AI.naive import naive_ai
from AI.v1_1 import v1_ai
from lib.texaspoker import State
from lib.texaspoker import Player

address = 'localhost'
port = 15000
key = 'NULL'
step = -1
initMoney = -1
bigBlind = -1
totalPlayer = -1
button = -1
state = State(totalPlayer, initMoney, bigBlind, button)

class Client(object):
    def __init__(self, u: str, AI):
        # the frame to put ui components on
        self.username = u
        # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        # self.request_iterator = ClientRequester()
        self.conn = rpc.GameStub(channel)
        self.ai = AI
        self._lock = threading.Lock()
        self._decision_so_far = []
        self._new_response = []
        self._new_request = []

    def chat_with_server(self):
        while True:
            if len(self._new_request) != 0:
                # self._lock.acquire()
                msg = self._new_request.pop(0)
                # self._lock.release()
                yield msg

    def run(self):

        while True:
            self.add_request(Client.HeartBeat())
            time.sleep(1)

    def start(self):
        """
        """
        global mypos
        global state
        global key
        global step
        global initMoney
        global bigBlind
        global totalPlayer
        global button

        # print('player position = ', mypos)
        # print('start in client begin')
        responses = self.conn.GameStream(self.chat_with_server())
        # print('reponses recieved by the client', mypos)
        for res in responses:
            # self._lock.acquire()
            # print('get a reponse from the server')
            self._new_response.append(res)
            # self._lock.release()
            if res.type == 2:
                # asking for a decision from the client
                state.currpos = res.pos
                if res.pos == mypos:

                    print('##### before decision, state and player:')
                    print(state)
                    print(state.player[mypos])
                   
                    decision = self.ai(mypos, state)
                    print('$$$ client made a decision:')
                    print(decision)
                    # self._lock.acquire()
                    self.add_request(dealer_pb2.DealerRequest(giveup=decision.giveup,
                    allin=decision.allin, check=decision.check, raisebet=decision.raisebet,
                    callbet=decision.callbet, amount=decision.amount, pos=mypos, type=1, token=key))
                    # self._lock.release()

            elif res.type == 1:
                # sending an info to the client to modify the state
                print('client received a decision info from the server')
                print('$$$ giveup,check,allin,callbet,raisebet,amount,pos:',res.giveup,res.check,res.allin,res.callbet,res.raisebet,res.amount, res.pos)
                state.currpos = res.pos
                self._decision_so_far.append(res)
                # update state
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
                    checkflag = 1

                elif res.raisebet == 1:
                    state.last_raised = res.amount - state.minbet
                    state.minbet = res.amount
                    delta = res.amount - state.player[state.currpos].bet
                    state.player[state.currpos].raisebet(delta)
                    state.moneypot += delta

                else:
                    print('impossible')

                print('##### after modify, state and player:')
                print(state)
                print(state.player[mypos])
                step += 1
                self._decision_so_far.append(res)

            elif res.type == 3:
                # state control command
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
                print('cards:', state.player[mypos].cards)
                for x in state.player[mypos].cards:
                    print(printcard(x), end='. ')
                print('\n')
                return
    def add_request(self, msg):
        # self._lock.acquire()
        self._new_request.append(msg)
        # self._lock.release()

    @staticmethod
    def HeartBeat():
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
        print('Error: enter the pos')
    mypos = int(sys.argv[1])


    username = 'bfan'
    c = Client(username, v1_ai)
    Job(c).start()
    c.start()
