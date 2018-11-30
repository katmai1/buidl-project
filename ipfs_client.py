import ipfsapi

from bitp2p import logger


class IPFSClient:

    def __init__(self):
        self.api = ipfsapi.connect("127.0.0.1", 5001)

    # ─── PEERS UTILS ────────────────────────────────────────────────────────────────
    
    def peer_is_connected(self, peer_id):
        for node in self.get_connected_peers():
            if peer_id == node['Peer']:
                return True
        return False

    def get_nodes_from_pubsub(self, pubsub):
        return self.api.pubsub_peers(pubsub)['Strings']

    def get_connected_peers(self):
        return self.api.swarm_peers()['Peers']

    def peer_disconnect(self, peer_id):
        for node in self.get_connected_peers():
            if peer_id == node['Peer']:
                return self.api.swarm_disconnect(f"{node['Addr']}/ipfs/{node['Peer']}")

    def new_peer(self, peer_id):
        info = self.api.id(peer_id)
        for address in info['Addresses']:
            if not self.peer_is_connected(peer_id):
                try:
                    r = self.api.swarm_connect(f"{address}/ipfs/{peer_id}")
                    if r['Strings'][0].endswith("success"):
                        logger.info("Conectado al peer: " + peer_id)
                        break
                except Exception:
                    pass