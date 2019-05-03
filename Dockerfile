FROM ubuntu:latest

RUN mkdir /app

COPY src/requirements.txt /app
COPY ./src /app/src
COPY . /app

WORKDIR /app/src



RUN apt-get update && apt-get install python3 python3-pip vim sqlite3 -y
RUN pip3 install -r requirements.txt




CMD ["python3", "app.py"]
