FROM ubuntu:latest

RUN mkdir /app

COPY src/requirements.txt /app
COPY ./src /app/src
COPY . /app

WORKDIR /app/src



RUN apt update && apt install python3 python3-pip vim sqlite3 sudo -y
RUN sudo apt install python-dev libpq-dev -y
RUN pip3 install -r requirements.txt




CMD ["python3", "app.py"]
