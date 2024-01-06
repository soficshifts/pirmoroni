# Clock example with NTP synchronization
#
# Create a secrets.py with your Wifi details to be able to get the time
# when the Galactic Unicorn isn't connected to Thonny.
#
# secrets.py should contain:
# WIFI_SSID = "Your WiFi SSID"
# WIFI_PASSWORD = "Your WiFi password"
#
# Clock synchronizes time on start, and resynchronizes if you press the A button

import time
import math
import random
import machine
import network
import ntptime
import WIFI_CONFIG
import uasyncio
import urequests
from galactic import GalacticUnicorn
from machine import Timer, Pin
from network_manager import NetworkManager
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY

# URL for Ecowitt (or compatible) API.
URL = '<set your URL here>'

# How often to refresh data in secons. If using a public API like Ecowitt, you should not call too often.
UPDATE_INTERVAL = 600

temperature=0.0
wind=0.0
rain_rate=4.0

# set up the Pico W's onboard LED
pico_led = Pin('LED', Pin.OUT)

# Connect to wifi and synchronize the RTC time from NTP
def sync_time():

    try:
        ntptime.settime()
        print("Time set")
    except OSError:
        print("time set error")
        pass


def status_handler(mode, status, ip):
    # reports wifi connection status
    print(mode, status, ip)
    print('Connecting to wifi...')
    if status is not None:
        if status:
            print('Wifi connection successful!  Setting Time')
        else:
            print('Wifi connection failed!')


def set_weather():
    #temperature = temperature+1.0
    #wind = (wind+5) % 25
    #print(f"temperature: {temperature}")
    #print(f"wind: {wind}")
    print(f"Requesting URL: {URL}")
    r = urequests.get(URL)
    # open the json data
    print("Data obtained!")
    set_weather_data(r.json())
    # lights will be set as part of main loop once data is set.
    r.close()
    
    # flash the onboard LED after getting data
    pico_led.value(True)
    time.sleep(0.2)
    pico_led.value(False)


def set_weather_data(data):
    global temperature
    global wind
    global rain_rate
    
    try:
        temperature = float(data['data']['outdoor']['feels_like']['value'])
    except:
        #print(e)
        print(" temperature failed")
        temperature=0
    
    try:
        wind = float(data['data']['wind']['wind_speed']['value'])
    except:
        #print(e)
        print("wind failed")
        wind=0
    
    try:
        rain_rate = float(data['data']['rainfall']['rain_rate']['value'])
    except:
        #print(e)
        print("rain failed")
        rain=0
    #print(f"data: temp: {temperature}; wind: {wind}; rain:{rain}")


# constants for controlling the background colour throughout the day
MIDDAY_HUE = 1.1
MIDNIGHT_HUE = 0.8
HUE_OFFSET = -0.1

MIDDAY_SATURATION = 1.0
MIDNIGHT_SATURATION = 1.0

MIDDAY_VALUE = 0.8
MIDNIGHT_VALUE = 0.3

yoffset = 1


# create galactic object and graphics surface for drawing
gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

# create the rtc object
rtc = machine.RTC()
last_milli = time.ticks_ms()

width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

# set up some pens to use later
WHITE = graphics.create_pen(255, 255, 255)
BLACK = graphics.create_pen(0, 0, 0)


'''
This method is Copyright (c) 2021 Pimoroni Ltd.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
@micropython.native  # noqa: F821
def from_hsv(h, s, v):
    i = math.floor(h * 6.0)
    f = h * 6.0 - i
    v *= 255.0
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)

    i = int(i) % 6
    if i == 0:
        return int(v), int(t), int(p)
    if i == 1:
        return int(q), int(v), int(p)
    if i == 2:
        return int(p), int(v), int(t)
    if i == 3:
        return int(p), int(q), int(v)
    if i == 4:
        return int(t), int(p), int(v)
    if i == 5:
        return int(v), int(p), int(q)

# Setup the overlays for rain & wind.
rain_array = [ [0,0,0] ] * width
rain_column =[[0 for i in range(0,height+4)] for j in range(0,width)]
#empty...will contain x positions of a triangle.
wind_row =[0 for i in range(0, width+10)]

def weather_background():
    #temperature=10.1   
    #0 = red;
    # 30 orange
    # 60 yellow
    # 120 blue-green
    # 180 cyan
    # 240 blue scaled 50 - 0.
    # start hue
    gradientStops = [240, 180, 60, 30, 0]
    gradientStop = 0;
    tempOffset = 0
	#Scale to the gradient stops.
    if (temperature < 10):
        gradientStop = 0
        stopUnit = 10
    elif (temperature < 20): #10<=temp<20)
        gradientStop = 1
        stopUnit=10
        tempOffset = 10
    elif (temperature < 30): #20<=temp<30)
        gradientStop = 2
        stopUnit=10
        tempOffset = 20
    else: # (30 <=temp < 50):
        gradientStop = 3
        stopUnit = 20
        tempOffset=30
    
    offset = (gradientStops[gradientStop] - gradientStops[gradientStop+1]) * ((temperature-tempOffset)/stopUnit)
    hue = (gradientStops[gradientStop]-offset)/360  
    #print(f"Temp: {temperature} Hue {hue}")
    sat=0.95 #0.5 + offset/20
    vol=0.45   
    backgroundPen = graphics.create_pen_hsv(hue, sat, vol)
    #for x in range(0, width):
    #    for y in range (0, height):
    #        graphics.pixel(x,y)
    rainandwind(backgroundPen, hue, sat, vol)
    #wind2()


'''
The method below is Copyright (c) 2021 Pimoroni Ltd

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
# function for drawing a gradient background
def gradient_background(start_hue, start_sat, start_val, end_hue, end_sat, end_val):
    half_width = width // 2
    for x in range(0, half_width):
        hue = ((end_hue - start_hue) * (x / half_width)) + start_hue
        sat = ((end_sat - start_sat) * (x / half_width)) + start_sat
        val = ((end_val - start_val) * (x / half_width)) + start_val
        colour = from_hsv(hue, sat, val)
        graphics.set_pen(graphics.create_pen(int(colour[0]), int(colour[1]), int(colour[2])))
        for y in range(0, height):
            graphics.pixel(x, y)
            graphics.pixel(width - x - 1, y)

    colour = from_hsv(end_hue, end_sat, end_val)
    graphics.set_pen(graphics.create_pen(int(colour[0]), int(colour[1]), int(colour[2])))
    for y in range(0, height):
        graphics.pixel(half_width, y)

# Does rain and wind effects.
def rainandwind(backgroundPen, hue, sat, vol):
    global rain_column
    
    #run array in reverse
    #drops can be four high.
    #rain_rate=99
    #wind=20.6
    drop_chance = min(rain_rate,100) / 500
    #rain colour
    rainPen = graphics.create_pen(0,0,255)
    
    #wind effect setup.
    windSpeed = min(20.7, wind)
    #windSpeed = max(0.2, wind)
    # Wind probability
    rustleLeaves = 0.5 * windSpeed / 20.7
    # Factor will set the "trob" of the LED @todo constants 0.55 max
    windFactor = min(1, windSpeed/20.7)
    
    windSat = max(0.15,windFactor)*sat #/0.25
    windVol = max(0.15,windFactor)*vol #/0.55
    #print(f"windSat {windSat} windVol {windVol}")
    #wind colour
    
    windPen = graphics.create_pen_hsv(hue,sat-windSat, vol-windVol)
    #windPen = graphics.create_pen(1,0,0)
    #wind effect from start only will be a random number.
    blow = random.uniform(0,1)
    start_index=width
    #determine if wind should blow
    if (wind_row[start_index-1]==0 and blow < rustleLeaves):
        #set the wind blow width based on wind speed.
        wind_width = round(9*random.uniform(rustleLeaves,1)) + 1
        #print(f"width {wind_width}")
        # Set how far wind will travel accross screen.
        wind_distance = max(1,round(width*windFactor))
        for z in range (start_index, len(wind_row)):
            if (wind_width == 0):
                wind_row[z]=0
            else:
                wind_row[z]=wind_distance
                wind_width = wind_width-1
        wind_row[width]=wind_distance
        #print(f"blow distance {wind_distance} correct {windVol}")
    start_index = height
    y1=0
    for x in range(0, width):
        usePen = backgroundPen
        #will a raindrop form?
        drop = random.uniform(0,1)
        # does the row have a wind effect? 
        windState = wind_row[x]
        #Wind in this colum???
        windpixel = wind_row[width-x-1]
        useWind =windpixel >0 and windpixel+height>x
        
        #print(x)
        #print(rain_column[x])
        if (rain_column[x][start_index]==0 and drop < drop_chance):
            #we may be able to add a drop here.
            if (rain_column[x][start_index-1] == 0):
                #drop allowed.
                drop_height = round(3*random.uniform(drop_chance,1)) + 1
                for z in range (start_index, len(rain_column[x])):
                    if (drop_height == 0):
                        rain_column[x][z]=0
                    else:
                        rain_column[x][z]=1
                        drop_height = drop_height-1
                #print(rain_column[x])
        #print(        
        #draw the column, then advance one.
        y=0
        for z in range(height,0,-1):
            usePen = backgroundPen
            if (rain_column[x][z]==1):
                usePen=rainPen                
            elif (useWind):
                #determine if wind needs to be used, it tapers.
                if (x<=windpixel): usePen = windPen
                elif (x<(windpixel+height) and y > (x-windpixel)): usePen=windPen                 
            graphics.set_pen(usePen)
            graphics.pixel(x,y)
            y=y+1
        # remove the last item
        rain_column[x].append(0)
        #print(rain_column[x])
        rain_column[x].pop(0)
    wind_row.append(0)
    wind_row.pop(0)

        
def wind2():
    global wind_column
    #wind effect setup.
    #windSpeed = min(20.7, wind)
    windSpeed = max(9, wind)
    # Wiind probability is "above" (rain is "below")
    rustleLeaves = 1 - 0.5 * windSpeed / 20.7
    # Factor will set the "trob" of the LED @todo constants 0.55 max
    windFactor = max(0, windSpeed/20.7)
    #triangle in center > 0
    start_index = width #allowing 10 wide
    for y in range(0,height):
        blow = random.uniform(0,1)
        column = wind_row[y]
        #print(x)
        #print(rain_column[x])
        for x in range(0,width):
            if (wind_row[y][start_index]==0 and blow > rustleLeaves):
                #potential wind line
                if (wind_row[y][start_index-1] == 0):
                    wind_width = round(9*random.uniform(rustleLeaves,1)) + 1
                    for z in range (start_index, len(wind_row[y])):
                        if (wind_width == 0):
                            wind_row[y][z]=0
                        else:
                            wind_row[y][z]=1
                            wind_width = wind_width-1
            
            #draw the column, then advance one.
            x=0
            for z in range(width-1,0,-1):
                if (wind_row[y][z]==1):
                    graphics.pixel(x,y)
                x=x+1
            # remove the last item
            wind_row[y].append(0)
            #print(rain_column[x])
            wind_row[y].pop(0)
    
'''Method below is Copyright (c) 2021 Pimoroni Ltd

MIT LICENSE

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''
# function for drawing outlined text
def outline_text(text, x, y):
    graphics.set_pen(BLACK)
    graphics.text(text, x - 1, y - 1, -1, 1)
    graphics.text(text, x, y - 1, -1, 1)
    graphics.text(text, x + 1, y - 1, -1, 1)
    graphics.text(text, x - 1, y, -1, 1)
    graphics.text(text, x + 1, y, -1, 1)
    graphics.text(text, x - 1, y + 1, -1, 1)
    graphics.text(text, x, y + 1, -1, 1)
    graphics.text(text, x + 1, y + 1, -1, 1)

    graphics.set_pen(WHITE)
    graphics.text(text, x, y, -1, 1)
    
# function for drawing outlined character...but use text function
def outline_char(text, x, y, reverse=False):
    
    if (text==":"):
        # no spaces on colon
        if (reverse):
            graphics.set_pen(BLACK)
        else:
            graphics.set_pen(WHITE)
        graphics.text(text, x, y, -1, 1)
        return 2
    #else:
    graphics.set_pen(BLACK)
    
    

    
    #the number 1 is the exception that needs an extra column
    if (text=="1"):
        x=x+1
        
    graphics.text(text, x - 1, y - 1, -1, 1)
    graphics.text(text, x, y - 1, -1, 1)
    graphics.text(text, x + 1, y - 1, -1, 1)
    graphics.text(text, x - 1, y, -1, 1)
    graphics.text(text, x + 1, y, -1, 1)
    graphics.text(text, x - 1, y + 1, -1, 1)
    graphics.text(text, x, y + 1, -1, 1)
    graphics.text(text, x + 1, y + 1, -1, 1)
    graphics.set_pen(WHITE)
    
    graphics.text(text, x, y, -1, 1)
    #fixed width
    return 7




# NTP synchronizes the time to UTC, this allows you to adjust the displayed time
# by one hour increments from UTC by pressing the volume up/down buttons
#
# We use the IRQ method to detect the button presses to avoid incrementing/decrementing
# multiple times when the button is held.
utc_offset = 10

up_button = machine.Pin(GalacticUnicorn.SWITCH_VOLUME_UP, machine.Pin.IN, machine.Pin.PULL_UP)
down_button = machine.Pin(GalacticUnicorn.SWITCH_VOLUME_DOWN, machine.Pin.IN, machine.Pin.PULL_UP)


def adjust_utc_offset(pin):
    global utc_offset
    if pin == up_button:
        utc_offset += 1
    if pin == down_button:
        utc_offset -= 1


up_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=adjust_utc_offset)
down_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=adjust_utc_offset)


year, month, day, wd, hour, minute, second, _ = rtc.datetime()

last_second = second

network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)
uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))
sync_time()
set_weather()

timer = Timer(-1)
timer.init(period=UPDATE_INTERVAL * 1000, mode=Timer.PERIODIC, callback=lambda t: set_weather())

# Check whether the RTC time has changed and if so redraw the display
def redraw_display_if_reqd():
    global year, month, day, wd, hour, minute, second, last_second, last_milli
    
    # To disable the auto on/off, just set these both to 25 or larger.
    TURN_ON_AT=6
    TURN_OFF_AT=23

    year, month, day, wd, hour, minute, second, _ = rtc.datetime()
    milli = time.ticks_ms()
    
    
    #print(last_milli)
    if True:
        offset = milli - last_milli
        yoffset = 0+(offset/120)
        hour = (hour + utc_offset) % 24
        if (hour == TURN_OFF_AT):
            #turn off display at 23:00
            switch_display(False)
        elif (hour == TURN_ON_AT):
            switch_display(True)
        time_through_day = (((hour * 60) + minute) * 60) + second
        percent_through_day = time_through_day / 86400
        percent_to_midday = 1.0 - ((math.cos(percent_through_day * math.pi * 2) + 1) / 2)
        #print(percent_to_midday)

        hue = ((MIDDAY_HUE - MIDNIGHT_HUE) * percent_to_midday) + MIDNIGHT_HUE
        sat = ((MIDDAY_SATURATION - MIDNIGHT_SATURATION) * percent_to_midday) + MIDNIGHT_SATURATION
        val = ((MIDDAY_VALUE - MIDNIGHT_VALUE) * percent_to_midday) + MIDNIGHT_VALUE
    
        if (use_background=="gradient"):
            gradient_background(hue, sat, val,
                            hue + HUE_OFFSET, sat, val)
        else:
            weather_background()
        #clock = "{:02}:{:02}:".format(hour, minute)
        #clockChar = list(clock)
        
        if second != last_second:
        #if (yoff > 10 or second != last_second):
            last_second = second
            last_milli = time.ticks_ms()
            yoffset=0
        
        #clock is two numbers and three colons
        startwidth = 6*6
        #print(width)
        x = int(width/2) + int(startwidth/2) 
        y = 2
        #print("start={:02}".format(x))
        
        #experiment with seconds.
        seconds="{:02}".format(second)
        tsec = seconds[0]
        sec = seconds[1]
        nxsec = (int(sec) + 1 ) % 10
        pvsec = (int(sec) - 1) % 10
        if (pvsec<0):
            pvsec = 9
        #print(yoffset)
        
        yoff=int(yoffset)
        
        # seconds first
        #ignore return as x stays fxed.
        outline_char(sec, x, yoff)
        # char is 8 plus 2 for outline=10
        outline_char(str(nxsec), x, yoff-10)
        x=x-outline_char(str(pvsec), x, yoff+10)
        
        #tens seconds        
        if (nxsec==0 and yoff>2):
            #flip the 10s.
            nx=int(tsec)+1 % 6
            #pv=int(tsec)-1 % 6
            #if (pv < 0):
            #    pv=5
            outline_char(str(nx), x, yoff-10)
            #outline_char(str(pv), x, yoff+10)
            x=x-outline_char(tsec, x, yoff)
        else:
            x = x-outline_char(tsec, x, y)
        
        #colon
        #print("seconds colon at {:02}".format(x))
        x=x-outline_char(":", x+4, y, second%2==0)
        
#        x=x-outline_char("5", x, y)
#        x=x-outline_char("5", x, y)
        #minutes
        minutes="{:02}".format(minute)
        tmin = minutes[0]
        mins = minutes[1]
        if (second > 58 and yoff>2):
            # flips the ones
            nx=int(mins)+1%10
            
            outline_char(str(nx), x, yoff-10)
            #outline_char(str(pv), x, yoff+10)
            x=x-outline_char(mins, x, yoff)
            #flip the tens
            if (int(mins)==9):
                nx = int(tmin)+1%6
                outline_char(str(nx), x, yoff-10)
                x=x-outline_char(tmin, x, yoff)
            else:
                x=x-outline_char(tmin, x, y)
        else:
            x = x-outline_char(mins, x, y)
            x = x-outline_char(tmin, x, y)
        #colon
        #print("colon at {:02}".format(x))
        x=x-outline_char(":", x+4, y, second%2==0)
        
        #hours
        hours="{:02}".format(hour)
        thr = hours[0]
        hr = hours[1]
        if (second > 58 and minute > 58 and yoff>2):
            # flips the ones
            flipthr =False;
            nx=int(hr)+1%10
            if (hour==23):
                nx=0;
            outline_char(str(nx), x, yoff-10)
            #outline_char(str(pv), x, yoff+10)
            x=x-outline_char(hr, x, yoff)
            #flip the tens
            if (hour == 19):
                nx = 2
                flipthr = True
            elif (hour == 23):
                nx = 0
                flipthr = True            
            elif (hour == 9):
                nx = 1
                flipthr = True
            if (not flipthr):
                x=x-outline_char(thr, x, y)
            else:
                outline_char(str(nx), x, yoff-10)
                x=x-outline_char(thr, x, yoff)
        else:
            x = x-outline_char(hr, x, y)
            x = x-outline_char(thr, x, y)
        
        # calculate text position so that it is centred
        #w = graphics.measure_text(clock, 1)
        #x = int(startwidth / 2 - w / 2 + 1)
        #y = 2

        #outline_text(clock, x, y)
    
        #yoffset=0
def switch_display(on):
    global display_on, brightness
    
    if (on and not display_on):
        gu.set_brightness(brightness)
        display_on = True
    elif (not (on and display_on)): #off
        brightnesss = gu.get_brightness()
        gu.set_brightness(0.0)
        display_on = False
    

# set the font
graphics.set_font("bitmap8")
gu.set_brightness(0.5)
brightness = gu.get_brightness()
display_on = True
use_background = "weather"



while True:
    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
        gu.adjust_brightness(+0.01)

    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
        gu.adjust_brightness(-0.01)

    if gu.is_pressed(GalacticUnicorn.SWITCH_A):
        sync_time()
    
    if gu.is_pressed(GalacticUnicorn.SWITCH_B):
        use_background="weather"
    
    if gu.is_pressed(GalacticUnicorn.SWITCH_C):
        use_background="gradient"
        
    if gu.is_pressed(GalacticUnicorn.SWITCH_D):
        switch_display(not display_on)
        
    redraw_display_if_reqd()
    
    # update the display
    gu.update(graphics)
    
    time.sleep(0.005)
