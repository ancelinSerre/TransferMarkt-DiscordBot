# syntax=docker/dockerfile:1

FROM python:3.9.5-slim-buster

WORKDIR /app

RUN apt-get update
RUN apt-get install -y locales locales-all
ENV LC_ALL fr_FR.UTF-8
ENV LANG fr_FR.UTF-8
ENV LANGUAGE fr_FR.UTF-8

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "bot.py"]