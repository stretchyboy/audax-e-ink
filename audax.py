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

# TODO : Proper timezone support not just adding 3600 seconds

if badger2040.is_wireless():
    import ntptime
    try:
        ntptime.settime()
        try:
            badger2040.pico_rtc_to_pcf()
        except RuntimeError:
           pass
    except (RuntimeError, OSError) as e:
        print(f"Wireless Error: {e.value}")

try:
    badger2040.pcf_to_pico_rtc()
except RuntimeError:
    pass

rtc = machine.RTC()

TEXT_SIZE = 1
LINE_HEIGHT = 16

# Display Setup
display = badger2040.Badger2040()
display.led(128)

# Connects to the wireless network. Ensure you have entered your details in WIFI_CONFIG.py :).
#display.connect()
#net = network.WLAN(network.STA_IF).ifconfig()

state = {
    "current_ride":0,
    "current_feature":0,
    "times":[]
}
badger_os.state_load("audax", state)

routes_data = {}
badger_os.state_load("audax_routes", routes_data)
routes = routes_data["routes"]

# Display Setup
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(2)

'''
# Setup buttons
button_a = machine.Pin(badger2040.BUTTON_A, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_b = machine.Pin(badger2040.BUTTON_B, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_c = machine.Pin(badger2040.BUTTON_C, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_down = machine.Pin(badger2040.BUTTON_DOWN, machine.Pin.IN, machine.Pin.PULL_DOWN)
button_up = machine.Pin(badger2040.BUTTON_UP, machine.Pin.IN, machine.Pin.PULL_DOWN)

button_next = button_down
button_prev = button_up
'''

#TODO : Menu of days and reload
#TODO : Calc Distance to go
#TODO : Page for feature

def getRemaining(total, dist):
    return total - dist

def getMeanGradient(feature):    
    if feature["dist_end"] == feature["dist_start"] :
        return 0
    return round(100 * (feature["elevation_end"] - feature["elevation_start"]) / (1000*(feature["dist_end"] - feature["dist_start"])))

def getETA(state):
    route = routes[state["current_ride"]]
    feature = route["features"][state["current_feature"]]
    
    if("dist" in feature):
        dist =  feature["dist"]
    if("dist_end" in feature):
        dist = feature["dist_end"]
        
    dur = 0
    if state["times"][state["current_ride"]][state["current_feature"]] > 0:
        dur = state["times"][state["current_ride"]][state["current_feature"]] - state["times"][state["current_ride"]][0]
    elif state["current_feature"] > 1:
        dur = state["times"][state["current_ride"]][state["current_feature"] -1] - state["times"][state["current_ride"]][0]
    
    if dur:
        speed = round(float(dist) / (float(dur) / 3600),1)
    else:
        speed = round(float(route["speeds"]["min"]),1)    
    
    if(speed == 0.0):
       speed = round(float(route["speeds"]["min"]),1)    
        
    print("speed", speed)
    
    hours = route["length"] / speed
    print ("hours", hours)
    eta = round(state["times"][state["current_ride"]][0] + ( hours * 3600.0 ))
    return speed, eta
    
    
#"start",
#"climb",
#"info",
#"receipt",
#"receipt_area",
#"end"

#TODO : Display dist and remaining

#TEXT_SIZE = 1
TEXT_SIZE = 2
#LINE_HEIGHT = 15
LINE_HEIGHT = 20


display = badger2040.Badger2040()
display.led(128)

def showFeature(state):
    route = routes[state["current_ride"]]
    feature = route["features"][state["current_feature"]]
    
    print("route", route)
    print("feature", feature)
    
    # Clear to white
    display.set_pen(15)
    display.clear()

    display.set_font("bitmap8")
    display.set_pen(0)
    display.rectangle(0, 0, WIDTH, 16)
    display.set_pen(15)
    display.text("audax-e-ink", 3, 4, WIDTH, 1)

    
    display.text(route["name"], WIDTH - display.measure_text(route["name"], 0.4) - 4, 4, WIDTH, 1)
    display.set_pen(0)
    y = 16 + int(LINE_HEIGHT / 2)
 
    display.text(feature["name"] + " : " + feature["type"].replace("_area", " ") , 5, y, WIDTH, TEXT_SIZE)
    y += LINE_HEIGHT
    
    if("dist" in feature):
        display.text("@ " + str(route["length"] - feature["dist"] ) + "km remaining" , 5, y, WIDTH, TEXT_SIZE)
        y += LINE_HEIGHT
    
    if("dist_start" in feature):
        display.text(str(route["length"] - feature["dist_start"] ) + "km - "+str(route["length"] - feature["dist_end"] ) +"km to go" , 5, y, WIDTH, TEXT_SIZE)
        y += LINE_HEIGHT
        
    if("elevation_start" in feature):
        display.text(str(round(feature["dist_end"] - feature["dist_start"],1) ) + "km @ "+str(getMeanGradient(feature)) +"% : " + str(feature["gradient_max"]) +" max" , 5, y, WIDTH, TEXT_SIZE)
        y += LINE_HEIGHT
 
    if("description" in feature):
        display.text(feature["description"], 5, y, WIDTH, TEXT_SIZE)
        y += LINE_HEIGHT
        
    if state["current_feature"] in state["times"][state["current_ride"]]:
        if state["times"][state["current_ride"]][state["current_feature"]] > 0:
            year, month, mday, hour, minute, second, weekday, yearday = time.gmtime(state["times"][state["current_ride"]][state["current_feature"] ] + 3600)
            hms = "Logged at {:02}:{:02}:{:02}".format(hour, minute, second)
            display.text(hms, 5, y, WIDTH, TEXT_SIZE)
            y += LINE_HEIGHT    
    
    
    #if state["current_feature"] > 0 :
    if state["times"][state["current_ride"]][0] > 0:
        speed, eta = getETA(state)
        year, month, mday, hour, minute, second, weekday, yearday = time.gmtime( eta+ 3600)
        print(year, month, mday, hour, minute, second)
        hms = "ETA {:02}:{:02}:{:02} @ {}kph".format(hour, minute, second, speed) 
        
        display.text(hms, 5, y, WIDTH, TEXT_SIZE)
        y += LINE_HEIGHT

    
    '''    
    year, month, day, wd, hour, minute, second, _ = time.localtime(time.mktime(rtc.datetime())+3600)
    hms = "{:02}:{:02}:{:02}".format(hour, minute, second)
    display.text(hms, 5, y, WIDTH, TEXT_SIZE)
    
    y += LINE_HEIGHT
    '''
       
changed = True

while len(state["times"]) <= state["current_ride"]:
    state["times"].append([])
while len(state["times"][state["current_ride"]]) <= state["current_feature"]:
    state["times"][state["current_ride"]].append(0)

        
# Call halt in a loop, on battery this switches off power.
# On USB, the app will exit when A+C is pressed because the launcher picks that up.
while True:
    display.keepalive()
    
    if display.pressed(badger2040.BUTTON_DOWN):
    #if(button_next.value()):
        if state["current_feature"] < len(routes[state["current_ride"]]["features"]) - 1:
            state["current_feature"] += 1
            changed = True
        elif state["current_ride"] < len(routes) - 1:
            state["current_feature"] = 0
            state["current_ride"] += 1
            changed = True
    
    if display.pressed(badger2040.BUTTON_UP):    
    #if(button_prev.value()):
        if state["current_feature"] > 0:
            state["current_feature"] -= 1
            changed = True
        elif state["current_ride"] > 0:
            state["current_ride"] -= 1
            state["current_feature"] = len(routes[state["current_ride"]]["features"]) - 1
            changed = True
    
    if display.pressed(badger2040.BUTTON_B):
        while len(state["times"]) <= state["current_ride"]:
            state["times"].append([])
        while len(state["times"][state["current_ride"]]) <= state["current_feature"]:
            state["times"][state["current_ride"]].append(0)
        
        
        year, month, day, wd, hour, minute, second, _ = rtc.datetime()

        state["times"][state["current_ride"]][state["current_feature"] ] = time.mktime((year, month, day, hour, minute, second, 0, 0))
        changed = True
        
        if state["current_feature"] < len(routes[state["current_ride"]]["features"]) - 1:
            state["current_feature"] += 1
            changed = True
        elif state["current_ride"] < len(routes) - 1:
            state["current_feature"] = 0
            state["current_ride"] += 1
            changed = True
    
        
    
    if changed:
        badger_os.state_save("audax", state)
        showFeature(state)
        display.update()
        display.set_update_speed(badger2040.UPDATE_FAST)
        changed = False
        
    display.halt()

