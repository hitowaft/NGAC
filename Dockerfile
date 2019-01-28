FROM ubuntu:latest

RUN mkdir /myapp
WORKDIR /myapp

COPY requirements.txt /myapp

RUN apt-get update && apt-get install python3 python3-pip vim -y

RUN pip3 install -r requirements.txt


EXPOSE 8080

CMD ["python3", "app.py"]
