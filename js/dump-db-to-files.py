#!/usr/bin/env python3
# Script for converting eddie format (sqlite, hashes) to joshua format (files, paths)

import sys
import os
_, filename = sys.argv

import sqlite3


uri = 'file:{}?mode=ro'.format(filename)
conn = sqlite3.connect(uri, uri=True)  # type: ignore

def iterate(conn):
        yield from (t for t in conn.execute('''
            SELECT source_file.hash, source_file.path, source_file.source
              FROM source_file 
              INNER JOIN usable_source ON usable_source.hash=source_file.hash
        '''))

paths = set()
hashes = set()

for corpuscle in iterate(conn):
    hash_, path, source = corpuscle
    if '.min.js' in path: 
        continue
    if path in paths:
        raise Exception("duplicate path")
    if hash_ in hashes:
        raise Exception("duplicate hash")
    paths.add(path)
    hashes.add(hash_)
    print(path)
    output_path = "javascript-sources/" + path
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as output_:
        output_.write(source)
