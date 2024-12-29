FROM ubuntu:24.04

RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11

WORKDIR /usr/src/app

COPY . .

RUN pip3 install -r requirements.txt \
    && pip3 install python-dotenv
