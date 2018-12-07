import threading
import subprocess
import os
import requests
import shutil
import ipfsapi
import time
import json
from pprint import pprint
from pathlib import Path


from bitp2p import logger


class IPFSCluster(threading.Thread):

    bootstrap = "/ip4/192.168.20.155/tcp/9096/ipfs/QmUAnGjgve8PsNdkSsBwfDrSxgfXrMrzgEhfKj13CPzbmt"
    secret = "de57552e3682afd6942a237df4ac58c8283c2dae6f1933da8aea5a2dcf9bc157"
    bootstrap_pool_address = "QmRvrDWLYAKZVR5swXqvVpiRzovJfYZZQVJYrpdHiiaPhi"

    links_server = {
        "386": "link",
        "amd64": "https://dist.ipfs.io/ipfs-cluster-service/v0.7.0/ipfs-cluster-service_v0.7.0_linux-amd64.tar.gz",
        "arm": "link",
        "arm64": ""
    }
    links_ctl = {
        "386": "link",
        "amd64": "https://dist.ipfs.io/ipfs-cluster-ctl/v0.7.0/ipfs-cluster-ctl_v0.7.0_linux-amd64.tar.gz",
        "arm": "link",
        "arm64": ""
    }

    def __init__(self, peer_id):
        threading.Thread.__init__(self)
        os.environ['CLUSTER_SECRET'] = self.secret
        self._api = ipfsapi.connect('127.0.0.1', 5001)
        self.bootstrap_list = {}
        self.peer_id = peer_id

    # ejecuta comandos, comprueba errores y salida estandard
    def cmd(self, cmd):
        r = subprocess.run("bin/ipfs-cluster-service " + cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        if r.stderr:
            logger.error(r.stderr.decode("utf-8"))
            return None
        if r.stdout:
            return r.stdout.decode("utf-8")
        return "OK"
    
    #
    def ctl(self, cmd):
        r = subprocess.run("bin/ipfs-cluster-ctl --enc json " + cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        if r.stderr:
            logger.error(r.stderr.decode("utf-8"))
            return None
        if r.stdout:
            return json.loads(r.stdout.decode("utf-8"))
        return "OK"

    def run(self):
        if os.environ['CLUSTER_GENESIS'] == "true":
            r = self.cmd("daemon")
        else:
            bootstrap_addr = self.get_bootstrap()
            for key in bootstrap_addr:
                try:
                    r = self.cmd(f"daemon --bootstrap {key}")
                    logger.info("Conectado al peer del cluster")
                except Exception as e:
                    logger.error("error al connectar al peer")

    # ─── METODOS ────────────────────────────────────────────────────────────────────
    def get_bootstrap(self):
        resolved_addr = self._api.resolve("/ipns/" + self.bootstrap_pool_address)['Path']
        return self._api.get_json(resolved_addr)

    def update_bootstrap_pool(self):
        from bitp2p import ipfsd
        bootstrap_id = self.ctl('id')['id']
        bootstraps = self.ctl('id')['addresses']
        self.bootstrap_list[bootstrap_id] = bootstraps
        new_addr = self._api.add_json(self.bootstrap_list)
        self._dd = self._api.name_publish(new_addr, resolve=False, lifetime="24h", key="nodes_pool")
        logger.info("Added peers into dns")
    
    # instala el binario de ipfs
    def install_server(self, arch="amd64"):
        # descargar tar.gz
        r = requests.get(self.links_server[arch])
        with open("/tmp/ipfs-cluster-service.tar.gz", "wb") as code:
            code.write(r.content)
        # descomprime
        shutil.unpack_archive('/tmp/ipfs-cluster-service.tar.gz', '/tmp/_ipfscs')
        os.system("mkdir -p bin")
        os.system("mv /tmp/_ipfscs/ipfs-cluster-service/ipfs-cluster-service bin/")
    
    def install_ctl(self, arch="amd64"):
        # descargar tar.gz
        r = requests.get(self.links_ctl[arch])
        with open("/tmp/ipfs-cluster-ctl.tar.gz", "wb") as code:
            code.write(r.content)
        # descomprime
        shutil.unpack_archive('/tmp/ipfs-cluster-ctl.tar.gz', '/tmp/_ipfscctl')
        os.system("mkdir -p bin")
        os.system("mv /tmp/_ipfscctl/ipfs-cluster-ctl/ipfs-cluster-ctl bin/")
    
    # crea la configuracion inicial para ipfs
    def init_config(self):
        r = self.cmd("init")

    # ─── PROPIEDADES ────────────────────────────────────────────────────────────────

    # @property
    # def is_active(self):
    #     try:
    #         self._api = ipfsapi.connect('127.0.0.1', 5001)
    #         return True
    #     except Exception:
    #         return False
    
    @property
    def is_installed(self):
        filebin = Path("bin/ipfs-cluster-service")
        if filebin.exists():
            return True
        return False

    @property
    def is_configured(self):
        fileconfig = Path(f"{os.environ['HOME']}/.ipfs-cluster/service.json")
        if fileconfig.exists():
            return True
        return False

def start_cluster_service(ipfsd):
    clusterd = IPFSCluster(ipfsd.peer_id)
    # check if installed
    if not clusterd.is_installed:
        logger.info("IPFS Cluster was not found. Downloading...")
        clusterd.install_server()
        clusterd.install_ctl()
    if not clusterd.is_configured:
        logger.info("IPFS Cluster initial config not found. Making initial config...")
        clusterd.init_config()
    clusterd.start()
    
    if os.environ['CLUSTER_GENESIS'] == "true":
        time.sleep(10)
        clusterd.update_bootstrap_pool()
    return clusterd
