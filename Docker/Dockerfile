FROM python:latest
MAINTAINER Peter Zhizhin <piter.zh@gmail.com>
ADD /../requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_U
ENV PYTHONIOENCODING=utf-8
WORKDIR /source
CMD python3 /source/main.py
