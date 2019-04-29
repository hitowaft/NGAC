FROM ubuntu:latest

RUN mkdir /app
WORKDIR /app

COPY src/requirements.txt /app

RUN apt-get update && apt-get install python3 python3-pip vim sqlite3 -y
RUN pip3 install -r requirements.txt


EXPOSE 8080

CMD ["python3", "src/app.py"]
