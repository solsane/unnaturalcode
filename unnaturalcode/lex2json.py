#!/bin/env python

from unnaturalcode import pythonSource

import os, sys, re, json

# parts taken from https://stackoverflow.com/questions/2212643/python-recursive-folder-read 2015-06-28
walk_dir = sys.argv[1]

#print('walk_dir = ' + walk_dir)

# If your current working directory may change during script execution, it's recommended to
# immediately convert program arguments to an absolute path. Then the variable root below will
# be an absolute path as well. Example:
# walk_dir = os.path.abspath(walk_dir)
#print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

datas = dict()

for root, subdirs, files in os.walk(walk_dir):
    #print('--\nroot = ' + root)

    #for subdir in subdirs:
        #print('\t- subdirectory ' + subdir)
    for filename in files:
        file_path = os.path.join(root, filename)
        #print('\t- file %s (full path: %s)' % (filename, file_path))
        match = re.search(r'./([\w\d.]+)/(.+\.py)', file_path)
        if match:
            version = match.group(1)
            fileish = match.group(2)
            print('file %s version %s' % (fileish, version))
            with open(file_path, 'rb') as f:
                f_content = f.read()
                lexed = pythonSource.pythonSource(f_content)
                scrubbed = lexed.scrubbed()
                toks = [bytes(tok.val + ":" + tok.type).decode('utf-8', 'replace') for tok in scrubbed]
                if fileish not in datas:
                    datas[fileish] = dict()
                datas[fileish][version] = toks

outfile = open('lexedversionstypes.json', 'wb')
json.dump(datas, outfile)  

