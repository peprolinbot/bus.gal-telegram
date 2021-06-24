FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev
    
COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install -r requirements.txt

COPY . /

RUN mkdir /etc/bus.gal-telegram

ENV BUS.GAL_DATABASE_PATH=/etc/bus.gal-telegram/database.db

ENTRYPOINT [ "python3" ]

CMD [ "main.py" ]

