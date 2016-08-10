#!/bin/bash
# Create a flat archive (so relative links work) and host it with a php server
# Params: <port> default 8888

port=${1-8888}

if [ -d "flat-archive" ]; then
    echo Flat archive exists
else
    echo Preparing a flat archive
    cp -r archive/ flat-archive/
    python -m scripts.make_flat flat-archive
fi

echo Running on port $port
php -S localhost:$port -t flat-archive