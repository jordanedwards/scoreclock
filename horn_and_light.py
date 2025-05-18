#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  horn_and_light.py
import time
import os
import RPi.GPIO as GPIO
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv

load_dotenv()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT) # This is pin 8, GPIO 14


def run():
    GPIO.output(8, GPIO.HIGH)  # Turn on the LED
    try:
        sound = AudioSegment.from_wav("horns/" + os.getenv('GOAL_HORN'))
        play(sound)
    except FileNotFoundError:
        print(f"Error: File not found: horns/{os.getenv('GOAL_HORN')}")
    except Exception as e:
        print(f"An error occurred: {e}")
    time.sleep(15)
    GPIO.output(8, GPIO.LOW)
    return None


run()