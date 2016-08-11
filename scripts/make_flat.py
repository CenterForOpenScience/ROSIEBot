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


def make_wiki_flat(subdir):
    wiki_home = subdir + '/wiki/home/index.html'
    if os.path.exists(wiki_home):
        shutil.copy(wiki_home, subdir + '/wiki/index.html')


def remove_organization():
    """
    Removes category folders and calls make_wiki_flat
    :return:
    """
    inflated_categories = ['project/', 'registration/', 'profile/']
    for category in inflated_categories:
        category_path = 'archive/' + category

        if not os.path.exists(category_path):
            continue

        if os.path.exists(category_path + '/.DS_Store'):
            os.remove(category_path + '/.DS_Store')

        subdirs = os.listdir(category_path)
        for dir in subdirs:
            make_wiki_flat(dir)
            shutil.move(category_path + dir, 'archive/' + dir)
        os.rmdir(category_path)

if __name__ == "__main__":
    print("Flattening:", mirror)

    remove_organization()