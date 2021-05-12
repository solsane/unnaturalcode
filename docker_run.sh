#!/usr/bin/env bash
docker run -it -p 5000:5000/tcp unnaturalcode --mount type=bind,src=$(pwd),dst=/work
