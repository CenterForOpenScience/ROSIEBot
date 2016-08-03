#!/bin/bash

cd ..
DATE=`date +%d`-2
python cli.py --scrape --nodes --institutions --users --registrations --dm=`date +%Y-%m-%dT%00:00:%00.00`