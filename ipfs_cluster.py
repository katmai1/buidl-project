import threading
import subprocess
import os
from pprint import pprint
from pathlib import Path


from bitp2p import logger


class IPFSCluster(threading.Thread):

    bootstrap = "/ip4/192.168.20.155/tcp/9096/ipfs/QmUAnGjgve8PsNdkSsBwfDrSxgfXrMrzgEhfKj13CPzbmt"
    secret = "de57552e3682afd6942a237df4ac58c8283c2dae6f1933da8aea5a2dcf9bc157"

    def __init__(self):
        threading.Thread.__init__(self)
        os.environ['CLUSTER_SECRET'] = self.secret
        # sino existe ninguna config la creamos
        fileconfig = Path(f"{os.environ['HOME']}/.ipfs-cluster/service.json")
        if not fileconfig.exists():
            r = self.cmd("init")

    # ejecuta comandos, comprueba errores y salida estandard
    def cmd(self, cmd):
        r = subprocess.run("./ipfs_bins/ipfs-cluster-service " + cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        if r.stderr:
            logger.error(r.stderr.decode("utf-8"))
            return None
        if r.stdout:
            return r.stdout.decode("utf-8")
        return "OK"

    def run(self):
        if os.environ['CLUSTER_FIRST'] == "true":
            r = self.cmd("daemon")
        else:
            r = self.cmd(f"daemon --bootstrap {self.bootstrap}")

def start_cluster_service():
    cluster = IPFSCluster()
    cluster.start()
    return cluster