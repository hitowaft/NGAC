FROM alpine:latest

RUN mkdir /app

COPY src/requirements.txt /app
COPY ./src /app/src
COPY . /app

WORKDIR /app/src



RUN apk add --update python3 py-pip vim sqlite sudo
RUN sudo apk add python3-dev postgresql-dev py-psycopg2
RUN pip3 install --upgrade -r requirements.txt




CMD ["python3", "app.py"]
