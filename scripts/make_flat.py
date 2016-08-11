#!/bin/python
"""
Make the organization of the mirror flat so that relative URLs cooperate
archive/project/mst3k -> archive/mst3k

:param 1 in CLI: folder to flatten
"""
import os
import shutil
import sys

mirror = 'archive/' if len(sys.argv) < 2 else sys.argv[1] + '/'

inflated_directories = ['project/', 'registration/']

print("Flattening:", mirror)

for directory in inflated_directories:

    path = 'archive/' + directory

    if not os.path.exists(path):
        continue

    if os.path.exists(path + '/.DS_Store'):
        os.remove(path + '/.DS_Store')

    subdirs = os.listdir(path)
    for dir in subdirs:
        shutil.move(path + dir, 'archive/' + dir)
    os.rmdir(path)
