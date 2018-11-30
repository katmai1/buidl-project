import os
import sys
import threading
import subprocess
import ipfsapi
import time
import socket
from pathlib import Path

from bitp2p import logger


# ─── DAEMON ─────────────────────────────────────────────────────────────────────
class IPFSDaemon(threading.Thread):
    
    errores = {
        "ipfs: not found": "IPFS no está instalado",
        "ipfs daemon is running": "IPFS ya está en marcha"
    }
    
    def __init__(self, PORT, PROTOCOL):
        threading.Thread.__init__(self)
        self.setName("IPFSD")
        self.p2p_protocol = "/x/myproto"
        self.port = PORT
        self.p2p_target = f"/ip4/127.0.0.1/{PROTOCOL}/{self.port}"
        self.stop()
    
    # ejecuta comandos, comprueba errores y salida estandard
    def cmd(self, cmd):
        r = subprocess.run(f"./ipfs_bins/ipfs {cmd}", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        if r.stderr:
            logger.error(r.stderr.decode("utf-8"))
            return None
        if r.stdout:
            return r.stdout.decode("utf-8")
        return "OK"
    
    # inicia el daemon
    def run(self):
        # sino existe ninguna config la creamos
        fileconfig = Path(f"{os.environ['HOME']}/.ipfs/config")
        if not fileconfig.exists():
            r = self.cmd("init")
        # ejecutamos el daemon
        r = self.cmd("daemon --enable-pubsub-experiment")

    # detiene el daemon
    def stop(self):
        os.system("pkill ipfs")


    # devuelve true si el daemon está activo
    @property
    def is_active(self):
        try:
            self._api = ipfsapi.connect('127.0.0.1', 5001)
            return True
        except Exception:
            return False

    # espera a que la conexion esté activa
    def wait_connection(self):
        while not self.is_active:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
    
    def configure(self):
        # activamos el p2pstream 
        r = self.cmd("config --json Experimental.Libp2pStreamMounting true")
        # cerramos los listen que puedan estar abiertos
        r = self.cmd("p2p close --all")
        # creamos nuestro listen
        r = self.cmd(f"p2p listen --allow-custom-protocol {self.p2p_protocol} {self.p2p_target}")

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
    if daemon.is_active:
        sys.exit("IPFS Daemon already running")
    daemon.start()
    daemon.wait_connection()
    daemon.configure()
    logger.info("IPFS Daemon started")
    return daemon
# ────────────────────────────────────────────────────────────────────────────────