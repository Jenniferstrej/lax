#!/bin/bash
source venv/bin/activate
pip-chill --all --verbose > chilled.txt
cat chilled.txt
