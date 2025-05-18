#!/bin/sh

sudo apt update
sudo apt install python3-pip python3-dev git libaugeas0 -y
sudo apt-get install python3-rpi.gpio -y
cp .env.example .env
chown pi /home/pi/scoreclock/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 load.py