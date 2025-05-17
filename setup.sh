#!/bin/sh

sudo apt update
sudo apt install python3-pip python3-dev git libaugeas0 -y
sudo apt-get install python3-rpi.gpio -y
python3 -m venv .venv
source .venv/bin/activate
cp ~/scoreclock/.env.example ~/scoreclock/.env