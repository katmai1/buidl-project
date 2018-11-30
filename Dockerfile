FROM python:3.7.0
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD ipfs_daemon.py ./
ADD bitp2p.py ./
ADD ipfs_events.py ./
COPY ipfs_bins ./ipfs_bins

CMD ["python", "bitp2p.py", "serve"]
