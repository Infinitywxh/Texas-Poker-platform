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
from lib.texaspoker import initMoney
from lib.texaspoker import bigBlind
from lib.texaspoker import totalPlayer
from lib.texaspoker import button
from AI.naive import naive_ai
import server
address = 'localhost'
port = 11912



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
        self._response_so_far = []
        self._request_so_far = []
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
        print('player position = ', mypos)
        # print('start in client begin')
        responses = self.conn.GameStream(self.chat_with_server())
        print('reponses recieved by the client')
        for res in responses:
            # self._lock.acquire()
            self._new_response.append(res)
            # self._lock.release()
            if res.type == 1:
                print('received a valid response, res:')
                print(res)
            else:
                print('receiced a empty response')
            if res.type == 1 and mypos == (res.pos + 1) % totalPlayer:
                print('client give a decision')
                decision = naive_ai(mypos, server.state)
                # self._lock.acquire()
                self.add_request(dealer_pb2.DealerRequest(giveup=decision.giveup,
                allin=decision.allin, check=decision.check, raisebet=decision.raisebet,
                callbet=decision.callbet, amount=decision.amount, pos=mypos, type=1))
                # self._lock.release()
            
    def add_request(self, msg):
        # self._lock.acquire()
        self._new_request.append(msg)
        # self._lock.release()

    @staticmethod
    def HeartBeat():
        global mypos
        return dealer_pb2.DealerRequest(command='heartbeat', type=0, pos=mypos)
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Error: enter the pos')
    mypos = int(sys.argv[1])
    username = 'bfan'
    c = Client(username, None)
    Job(c).start()
    c.start()
