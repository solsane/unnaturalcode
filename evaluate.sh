#!/bin/bash

set -ex

PARTITION="${1:?Must provide partition number}"
if [ $# -gt 1 ]; then
	DEVICE="device=gpu$2"
fi

THEANO_FLAGS="${DEVICE:-}"\
       	python unnaturalcode/validation/languages/java.py\
	-P 11000\
	--tool sensibility\
	--discard-identifiers\
       	--mutation null\
	--keep-corpus\
       	--pair-file-list test_files\
	--output-dir "results.$PARTITION"  # Misnomer: this is the results dir.
