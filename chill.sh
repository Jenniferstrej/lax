#!/bin/bash
./install.sh
source venv/bin/activate
pip-chill --all --verbose > chilled.txt
cat chilled.txt
