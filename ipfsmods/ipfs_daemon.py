# ──────────────────────────────────────────────────────────────────────────────────── I ──────────
#   :::::: S H I T   I P F S   D A E M O N   C L A S S : :  :   :    :     :        :          :
# ──────────────────────────────────────────────────────────────────────────────────────────────
#  original ipfs daemon only is available for Go! and NodeJS, this is a custom shit binding...
#

import os
import sys
import threading
import subprocess
import ipfsapi
import time
import socket
import requests
import shutil
from uuid import uuid4
from pathlib import Path

from bitp2p import logger

# ─── DAEMON ─────────────────────────────────────────────────────────────────────

class IPFSDaemon(threading.Thread):

    nodes_pool_address = "QmRvrDWLYAKZVR5swXqvVpiRzovJfYZZQVJYrpdHiiaPhi"
    
    # the CID is "QmRHEymXX6dVvZFvMe1qbNUZvHp5nFXuEf7YHP6VoUBZRE"
    links = {
        "386": "link",
        "amd64": "https://dist.ipfs.io/go-ipfs/v0.4.18/go-ipfs_v0.4.18_linux-amd64.tar.gz",
        "arm": "link",
        "arm64": ""
    }

    def __init__(self, PORT, PROTOCOL):
        threading.Thread.__init__(self)
        self.node_id = uuid4().hex
        self.setName("IPFSD")
        self.p2p_protocol = "/x/myproto"
        self.port = PORT
        self.nodes_list = {}
        self.p2p_target = f"/ip4/127.0.0.1/{PROTOCOL}/{self.port}"
        self.stop()

    # ─── BASIC METHODS ──────────────────────────────────────────────────────────────

    # inicia el daemon
    def run(self):
        r = self.cmd("daemon --enable-pubsub-experiment")

    # detiene el daemon
    def stop(self):
        os.system("pkill ipfs")
    
    # ejecuta comandos, comprueba errores y salida estandard
    def cmd(self, cmd):
        r = subprocess.run(f"./bin/ipfs {cmd}", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        if r.stderr:
            logger.error(r.stderr.decode("utf-8"))
            return None
        if r.stdout:
            return r.stdout.decode("utf-8")
        return "OK"
 
    # ─── OTHER METHODS ────────────────────────────────────────────────────────────────────
    def connect_nodes_list(self):
        for key in self.nodes_list:
            if key != self.peer_id:
                try:
                    res = self._api.swarm_connect(f"/p2p-circuit/ipfs/{key}", )
                    logger.info(f"Connectado al peer {key}")
                except Exception as e:
                    logger.error(f"Error al conectar con el peer {key}")

    def update_node_pool(self):
        self.nodes_list = self.get_peers_from_pool()
        self.connect_nodes_list()
        self.put_peers_to_pool()

    def get_peers_from_pool(self):
        logger.info("Obteniendo peers... (puede tardar algun minuto)")
        resolved_addr = self._api.name_resolve(self.nodes_pool_address)['Path']
        return self._api.get_json(resolved_addr)
    
    def put_peers_to_pool(self):
        self.nodes_list[self.peer_id] = self.node_id
        new_addr = self._api.add_json(self.nodes_list)
        self._dd = self._api.name_publish(new_addr, resolve=False, lifetime="24h", key="nodes_pool")
        logger.info("Added peers into dns")

    # espera a que la conexion esté activa
    def wait_connection(self):
        while not self.is_active:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
    
    # raw config daemon
    def configure_options(self):
        # activamos el p2pstream 
        r = self.cmd("config --json Experimental.Libp2pStreamMounting true")
        # activamos relayhop
        r = self.cmd("config --json Swarm.EnableRelayHop true")
        # cerramos los listen que puedan estar abiertos
        r = self.cmd("p2p close --all")
        # creamos nuestro listen
        r = self.cmd(f"p2p listen --allow-custom-protocol {self.p2p_protocol} {self.p2p_target}")
        os.system(f"cp ipfsmods/nodes_pool {os.environ['HOME']}/.ipfs/keystore/")

    # instala el binario de ipfs
    def install(self, arch="amd64"):
        # descargar tar.gz
        r = requests.get(self.links[arch])
        with open("/tmp/ipfs.tar.gz", "wb") as code:
            code.write(r.content)
        # descomprime
        shutil.unpack_archive('/tmp/ipfs.tar.gz', '/tmp/_ipfs')
        os.system("mkdir -p bin")
        os.system("mv /tmp/_ipfs/go-ipfs/ipfs bin/")
    
    # crea la configuracion inicial para ipfs
    def init_config(self):
        r = self.cmd("init")

    # ─── PROPIEDADES ────────────────────────────────────────────────────────────────

    @property
    def peer_id(self):
        return self._api.id()['ID']

    # devuelve true si el daemon está activo
    @property
    def is_active(self):
        try:
            self._api = ipfsapi.connect('127.0.0.1', 5001)
            return True
        except Exception:
            return False
    
    @property
    def is_installed(self):
        filebin = Path("bin/ipfs")
        if filebin.exists():
            return True
        return False

    @property
    def is_configured(self):
        fileconfig = Path(f"{os.environ['HOME']}/.ipfs/config")
        if fileconfig.exists():
            return True
        return False
    # ────────────────────────────────────────────────────────────────────────────────


    # @property
    # def peer_id(self):
    #     #return self.cmd("id -f '<id>\n'")
    #     return self._api.id()['ID']

    # # my listen address
    # @property
    # def my_listen_address(self):
    #     lista = self.p2p_ls()
    #     for l in lista:
    #         if l['Target'] == self.p2p_target:
    #             return l['Listen']
    #     return None
    # # devuelve lista json de los listeners
    # def p2p_ls(self):
    #     r = self.cmd('./ipfs_bins/ipfs p2p ls')
    #     if r:
    #         raw = r.split("\n")
    #         lista = []
    #         for listener in raw:
    #             if listener != "":
    #                 l = listener.split(" ")
    #                 d = { "Protocol": l[0], "Listen": l[1], "Target": l[2] }
    #                 lista.append(d)
    #         return lista
    #     return

    # def forward_close(self):
    #     r = self.cmd(f"./ipfs_bins/ipfs p2p close -l {self.p2p_forward}")

    # def forward_open(self, peer_id):
    #     r = self.cmd(f"./ipfs_bins/ipfs p2p forward {self.p2p_protocol} {self.p2p_forward} {peer_id}")
    
    # def anuncia_peer(self):
    #     logger.debug("Anunciando: " + self.peer_id)
    #     self._api = ipfsapi.connect('127.0.0.1', 5001)
    #     self._api.pubsub_pub("E75FnyzdD7TNZhGnWDt5mrTHF1/BitP2P", f"/newnode/{self.peer_id}")
# ────────────────────────────────────────────────────────────────────────────────


# ─── IPFS DAEMON STARTING ────────────────────────────────────────────────────────────

def start_ipfsd(port, protocol):
    daemon = IPFSDaemon(port, protocol)
    # check if installed
    if not daemon.is_installed:
        logger.info("IPFS was not found. Downloading...")
        daemon.install()
    if not daemon.is_configured:
        logger.info("IPFS initial config not found. Making initial config...")
        daemon.init_config()
    if daemon.is_active:
        daemon.stop()
        sys.exit("IPFS Daemon already running. Killing process...")
    daemon.start()
    daemon.wait_connection()
    daemon.configure_options()
    logger.info("IPFS Daemon started")
    daemon.update_node_pool()
    return daemon

# ────────────────────────────────────────────────────────────────────────────────