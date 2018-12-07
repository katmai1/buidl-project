FROM python:3.7.0
ADD . ./
RUN pip install -r requirements.txt
ENV CLUSTER_GENESIS false
ENV CLUSTER_SECRET de57552e3682afd6942a237df4ac58c8283c2dae6f1933da8aea5a2dcf9bc157
EXPOSE 9096
EXPOSE 9094
EXPOSE 9095
CMD ["python", "bitp2p.py", "serve"]