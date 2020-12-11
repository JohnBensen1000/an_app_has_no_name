FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /app_backend

WORKDIR /app_backend

ADD . /app_backend/

RUN pip install -r requirements.txt