import threading
import ipfsapi
from base64 import b64decode
import schedule
import time

from bitp2p import logger, PUBSUB


class IPFSEvents(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setName("IPFSEvents")
        self.api = ipfsapi.connect("127.0.0.1", 5001)
        self.pubsub = PUBSUB

    def handler(self, mensaje):
        m = mensaje.split("/")
        if m[1] == "newnode":
            logger.warning("els nodes ja no s'afegeixin aixi!!")
            # self.new_peer(m[2])

    def run(self):
        sub = self.api.pubsub_sub(self.pubsub)
        for msg in sub:
            self.handler(b64decode(msg['data']).decode("utf-8"))


# def start_schedule():
#     schedule.every(5).minutes.do(ipfsd.anuncia_peer)
#     while True:
#         schedule.run_pending()
#         time.sleep(5)