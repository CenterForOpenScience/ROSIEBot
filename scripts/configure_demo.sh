#!/bin/bash
cd scripts
cp demo_settings.py ../settings.py
cp demo_crawler.py ../crawler.py
cp demo_cli.py ../cli.py
cp ../archive/index.html ../demo_archive/index.html
cp ../archive/search.html ../demo_archive/search.html
cp -r mst3k ../demo_archive/project
cp -r 2qj6a ../demo_archive/profile
echo 'Demo files configured'
cd ..
doitlive play ./scripts/demo.sh -s 200