FROM python:3.6

LABEL MAINTAINER="Aiden Rutter <arutter@utk.edu>"

ENV ESTIMATENGRAM="/usr/local/bin/estimate-ngram"
ENV LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
# RUN apt update && apt install libzmq-dev automake autoconf gfortran python-virtualenv
RUN pip install -r requirements.txt

# must set the path for the following JS compilers:
# javascript: babel, v8, ESLint, JavaScriptCore

# add unnaturalcode to path
EXPOSE 5000
RUN python -m unnaturalcode.http
# run the tests