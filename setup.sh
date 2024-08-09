#!/bin/sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp -n config.json.example config.json