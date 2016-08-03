#!/bin/bash
python cli.py --scrape --nodes -dfwark --registrations --users --institutions --dm=2014-01-01T00:00:00.00
python cli.py --verify --rn=1 --tf=demo_taskfile.json
open demo_archive
php -S localhost:12345 -t demo_archive
