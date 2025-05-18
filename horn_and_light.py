#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  horn_and_light.py
#

import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT) # This is pin 8, GPIO 14


def play():
    GPIO.output(8, GPIO.HIGH)  # Turn on the LED
    time.sleep(3)
    GPIO.output(8, GPIO.LOW)
    time.sleep(3)
