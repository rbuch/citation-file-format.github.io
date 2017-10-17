#!/bin/bash

# enable error reporting to the console
set -e

# Run the Python script that converts all specifications.md files to PDF
python3 build-pdfs.py

## push
cd _site
git config user.email "travis-ci@sdruskat.net"
git config user.name "Travis CI"
git add --all
git commit -a -m "Travis #$TRAVIS_BUILD_NUMBER"
git push --force origin master
