FROM python:2

LABEL MAINTAINER="Aiden Rutter <arutter@utk.edu>"

# create user/group
# RUN groupadd -r unnaturalcode && useradd --no-log-init -r -g unnaturalcode unnaturalcode

# make a copy of the project
# TODO: cloning from git might be more appropriate but I also wanted to
# incorporate any local changes on build at least
COPY . /work
WORKDIR /work

RUN apt-get -y update && apt-get -y install libzmq3-dev automake autoconf gfortran python-virtualenv swig build-essential

# symptom: file not found in makefile (pymitlm/mitlm/.libs)
# try cleaning files b4 copy?
# problem: .dockerignore doesn't acct for the other .gitignore files
# RUN ls
RUN pip install /work

# env
ENV ESTIMATENGRAM="/usr/local/bin/estimate-ngram"
ENV LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
# must set the path for the following JS compilers:
# javascript: babel, v8, ESLint, JavaScriptCore

# add unnaturalcode to path
EXPOSE 5000
ENTRYPOINT [ "python", "-m", "unnaturalcode.http" ]
# ENTRYPOINT [ "/bin/bash" ]
# run the tests
# CMD python -m pytest .
