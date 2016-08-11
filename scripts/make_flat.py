#!/bin/python
"""
Produces a flat_archive version of the archive without OSF category folders registration, profile, and project, so that relative URLs cooperate

archive/project/mst3k -> archive/mst3k

WARNING: Utilities will not work with a flattened archive 

:param 1 in CLI: folder to flatten
"""
import os
import shutil
import sys

mirror = 'archive/' if len(sys.argv) < 2 else sys.argv[1] + '/'

inflated_directories = ['project/', 'registration/', 'profile/']

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
