FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y python mercurial python-pip
RUN apt-get install -y python-matplotlib

WORKDIR /
RUN hg clone https://bitbucket.org/timsn/tetrisagent
WORKDIR tetrisagent
#RUN pip install -r requirements.txt BitVector --allow-external BitVector --allow-unverified BitVector
RUN pip install -r requirements.txt --allow-external BitVector --allow-unverified BitVector
RUN python gui.py

