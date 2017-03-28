#!/usr/bin/env python3
# Script for converting eddie format (sqlite, hashes) to joshua format (files, paths)

import sys
import os
_, dbfilename = sys.argv

import sqlite3

utf8stdout = open(1, 'w', encoding='utf-8', closefd=False) # fd 1 is stdout


conn = sqlite3.connect(dbfilename)  # type: ignore

for hash_ in map(str.rstrip, sys.stdin):
    if hash_ == "":
        continue
    results = conn.execute('''
        SELECT path FROM source_file
        WHERE hash = ?
      ''', (hash_,)).fetchone()
    #print(hash_, file=sys.stderr)
    x = u"javascript-sources/" + results[0]
    print(x, file=utf8stdout)