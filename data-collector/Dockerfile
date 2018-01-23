FROM python:3-alpine

RUN apk update
RUN apk add g++ make postgresql-dev

COPY requirements.txt /app/

WORKDIR /app

RUN pip install -r /app/requirements.txt

COPY entrypoint.sh /app/
COPY data_collector.py /app/

ENTRYPOINT ./entrypoint.sh