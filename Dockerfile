FROM python:3.7.0
ADD . ./
RUN pip install -r requirements.txt

CMD ["python", "bitp2p.py", "serve"]