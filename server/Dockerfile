FROM tiangolo/uvicorn-gunicorn:python3.11-slim

LABEL maintainer="Ryan D'Mello <ryan.dmello.86@gmail.com>"

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY ./app /opt/ai_assistance/server
