FROM python:2

LABEL MAINTAINER="Aiden Rutter <arutter@utk.edu>"

RUN add-apt-repository universe && apt-get update && apt-get install libzmq3-dev automake autoconf gfortran python-virtualenv swig
RUN python -m pip install --upgrade pip
# create user/group
# RUN groupadd -r unnaturalcode && useradd --no-log-init -r -g unnaturalcode unnaturalcode

# make a copy of the project
# TODO: cloning from git might be more appropriate but I also wanted to 
# incorporate any local changes on build at least
COPY . /work
WORKDIR /work
RUN /usr/bin/yes | pip install -e /work

# env
ENV ESTIMATENGRAM="/usr/local/bin/estimate-ngram"
ENV LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
# must set the path for the following JS compilers:
# javascript: babel, v8, ESLint, JavaScriptCore

# add unnaturalcode to path
EXPOSE 5000
ENTRYPOINT [ "python", "-m", "unnaturalcode.http" ]

# run the tests
CMD python -m pytest .