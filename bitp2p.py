"""
Projecte

Usage:
  projecte.py serve

Options:
  -h --help      Show this screen.
"""
import os
import sys
import threading
import subprocess
import time
import logging
import coloredlogs
import ipfsapi
import socketserver
import socket
import random
from pprint import pprint
from docopt import docopt
from base64 import b64decode

# from utils import serialize, deserialize


# ─── CONFIG ─────────────────────────────────────────────────────────────────────
PORT = 10000
PROTOCOL = "tcp"
PUBSUB = "E75FnyzdD7TNZhGnWDt5mrTHF1/BitP2P"
# ────────────────────────────────────────────────────────────────────────────────


# ─── LOGGER ─────────────────────────────────────────────────────────────────────
os.environ["COLOREDLOGS_LOG_FORMAT"] = '%(threadName)s %(levelname)s %(message)s'
logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', logger=logger)
# ────────────────────────────────────────────────────────────────────────────────

ipfsd = None

# ─── MAIN ───────────────────────────────────────────────────────────────────────
def main(args):
    if args['serve']:
        # ipfs daemon
        global ipfsd
        from ipfsmods.ipfs_daemon import start_ipfsd
        ipfsd = start_ipfsd(PORT, PROTOCOL)
        # pprint(ipfsd.search_peers_by_cid())
        # cluster
        # from ipfs_cluster import IPFSCluster
        # cluster = IPFSCluster()
        # cluster.start()
        
        # ipfs events
        from ipfsmods.ipfs_events import IPFSEvents  #, start_schedule
        ipfs_events = IPFSEvents()
        ipfs_events.start()
        
        # busca los nodos activos y se conecta
        # from ipfs_client import IPFSClient
        # client = IPFSClient()

        #pprint(client.peer_disconnect("QmSBqTujbU2cti6RTEy9VXnep7RGZVxJqYMuLSeeX2sc3Q"))
        
        # all_peers = client.get_nodes_from_pubsub(PUBSUB)
        # pprint(all_peers)
        
        # for peer in all_peers:
        #     if client.peer_is_connected(peer):
        #         logger.info("PEER Ya conectado")
        #     else:
        #         logger.info("Conectando al peer")


        # # schedule
        # thread_schedule = threading.Thread(target=start_schedule, name="Scheduler")
        # thread_schedule.start()
        # #
        # time.sleep(5)
        # ipfsd.anuncia_peer()
        
    else:
        logger.error("Invalid command")

if __name__ == "__main__":
    main(docopt(__doc__))