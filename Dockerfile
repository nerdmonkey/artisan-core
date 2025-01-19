FROM ubuntu:24.04

RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip libffi-dev libssl-dev gcc make g++ \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

WORKDIR /usr/src/app

COPY . .

ENV BLIS_ARCH generic

RUN apt-get remove -y python3-cryptography \
    && pip3 install --no-cache-dir -r requirements.txt
