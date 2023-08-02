import gc
import os
import time
import math
import badger2040
import badger_os
import jpegdec
from badger2040 import WIDTH
import network
import machine
from urllib import urequest

TEXT_SIZE = 1
LINE_HEIGHT = 16

# Display Setup
display = badger2040.Badger2040()
display.led(128)

# Connects to the wireless network. Ensure you have entered your details in WIFI_CONFIG.py :).
display.connect()
net = network.WLAN(network.STA_IF).ifconfig()

state = {
    "current_ride":0,
    "current_feature":0,
}

badger_os.state_load("audax", state)


# Display Setup
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(2)

# Setup buttons
button_a = machine.Pin(badger2040.BUTTON_A, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_b = machine.Pin(badger2040.BUTTON_B, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_c = machine.Pin(badger2040.BUTTON_C, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_down = machine.Pin(badger2040.BUTTON_DOWN, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_up = machine.Pin(badger2040.BUTTON_UP, machine.Pin.IN, machine.Pin.PULL_DOWN)


#TODO : Menu of days and reload
#TODO : Calc Distance to go
#TODO : Page for feature

def getRemaining(total, dist):
    return total - dist

def getMeanGradient(start_dist, end_dist, start_ele, end_ele):
    if end_dist == start_dist :
        return 0
    return 100 * (end_ele - start_ele) / (1000*(end_dist - start_dist))


#TODO : Display Feature
#TODO : Name


#TODO : Display dist and remaining
