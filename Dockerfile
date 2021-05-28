# syntax=docker/dockerfile:1

FROM python:3.9.5-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python3 -m pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "bot.py"]