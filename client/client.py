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
                print(msg)
                yield msg

    def start(self):
        """
        """
        responses = self.conn.GameStream(self.chat_with_server())
        for res in responses:
            print(res)

    def run(self):
        while True:
            self.add_request(Client.HeartBeat())
            time.sleep(1)

    def add_request(self, msg):
        self._lock.acquire()
        self._new_request.append(msg)
        self._lock.release()

    @staticmethod
    def HeartBeat():
        return dealer_pb2.DealerRequest(command='heartbeat')


if __name__ == '__main__':
    username = 'bfan'
    c = Client(username, None)
    Job(c).start()
    c.start()
