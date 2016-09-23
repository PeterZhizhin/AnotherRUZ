FROM python:latest
MAINTAINER Peter Zhizhin <piter.zh@gmail.com>
ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
ENV PYTHONIOENCODING=utf-8
WORKDIR /source
CMD python3 /source/main.py
