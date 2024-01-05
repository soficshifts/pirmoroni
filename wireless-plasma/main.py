import WIFI_CONFIG
from network_manager import NetworkManager
import uasyncio
import urequests
import plasma
import network
import socket
import time
import random
from plasma import plasma_stick
from random import randrange, uniform
from machine import Timer, Pin

NUM_LEDS=50

led_strip = plasma.WS2812(NUM_LEDS, 0, 0, plasma_stick.DAT, color_order=plasma.COLOR_ORDER_RGB)

led_strip.start()

# light
light = True

# set up the Pico W's onboard LED
pico_led = Pin('LED', Pin.OUT)

# some variables we'll use for animations
ANIMATION_SPEED = 0.005  # higher number gets from current to target colour faster.  <1 for hsv
FLASH_SPEED = 1 #integer values for RGB

# Set this to how often you'll refresh data from the API in seconds
UPDATE_INTERVAL = 600

# URL to get the data from.  Data must be returned in Ecowitt format.
URL="<place your ecowitt or custom URL here>"

# Create an list of [r, g, b] values that will hold current LED colours, for display
current_leds = [[0] * 3 for i in range(NUM_LEDS)]
# Create an list of [r, g, b] values that will hold target LED colours, to move towards
target_leds = [[0] * 3 for i in range(NUM_LEDS)]
# Create an list of [r, g, b] values that will hold base  LED colours, to rest
base_leds = [[0] * 3 for i in range(NUM_LEDS)]
# Create a mode 0=nothing, 1=flash, 2=pulse
mode_leds = [0 for i in range(NUM_LEDS)]


baseToTarget = True
temperature = 31.2
wind=0.9
rain=0

def set_weather_data(data):
    global temperature
    global wind
    global rain
    
    try:
        temperature = float(data['data']['outdoor']['feels_like']['value'])
    except:
        #print(e)
        print(" temp failed")
        temperature=0
    
    try:
        wind = float(data['data']['wind']['wind_speed']['value'])
    except:
        #print(e)
        print("wind failed")
        wind=0
    
    try:
        rain = float(data['data']['rainfall']['rain_rate']['value'])
    except:
        #print(e)
        print("rain failed")
        rain=0
    
    
    print(f"data: temp: {temperature}; wind: {wind}; rain:{rain}")


def move_to_target_hsv():
    global baseToTarget
    # nudge our current colours closer to the target colours
    for i in range(NUM_LEDS):
        mode = mode_leds[i]
        flash = (mode==1)
        if (flash):
            speed = FLASH_SPEED
        else:
            speed = ANIMATION_SPEED
        for c in range(3):  # 3 times, for R, G & B channels
            if (mode == 0):
                current_leds[i][c] = base_leds[i][c]
            elif (flash):
                #flas is RGB.
                if current_leds[i][c] < target_leds[i][c]:
                    current_leds[i][c] = min(current_leds[i][c] + speed, target_leds[i][c])  # increase current, up to a maximum of target
                elif current_leds[i][c] > target_leds[i][c]:
                    current_leds[i][c] = max(current_leds[i][c] - speed, target_leds[i][c])  # reduce current, down to a minimum of target
                else: #back to base
                    current_leds[i][c] = base_leds[i][c]
            
            elif (baseToTarget):
                if current_leds[i][c] < target_leds[i][c]:
                    current_leds[i][c] = min(current_leds[i][c] + speed, target_leds[i][c])  # increase current, up to a maximum of target
                elif current_leds[i][c] > target_leds[i][c]:
                    current_leds[i][c] = max(current_leds[i][c] - speed, target_leds[i][c])  # reduce current, down to a minimum of target
                else: #back to base
                    baseToTarget = not baseToTarget
                    if (flash): #reset
                        current_leds[i][c] = base_leds[i][c]
            else: #target to base
                if current_leds[i][c] < base_leds[i][c]:
                    current_leds[i][c] = min(current_leds[i][c] + speed, base_leds[i][c])  # increase current, up to a maximum of target
                elif current_leds[i][c] > base_leds[i][c]:
                    current_leds[i][c] = max(current_leds[i][c] - speed, base_leds[i][c])  # reduce current, down to a minimum of target
                else: #back to base
                    baseToTarget = not baseToTarget
                
             
        #print(f"led={current_leds[i][c]}")
def set_colour_and_effect(mode, index, temp, windFactor=0):
    mode_leds[index]=mode
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
    if (temp < 10):
        gradientStop = 0
        stopUnit = 10
    elif (temp < 20): #10<=temp<20)
        gradientStop = 1
        stopUnit=10
        tempOffset = 10
    elif (temp < 30): #20<=temp<30)
        gradientStop = 2
        stopUnit=10
        tempOffset = 20
    else: # (30 <=temp < 50):
        gradientStop = 3
        stopUnit = 20
        tempOffset=30
    
    offset = (gradientStops[gradientStop] - gradientStops[gradientStop+1]) * ((temp-tempOffset)/stopUnit)
    hue = (gradientStops[gradientStop]-offset)/360  
    #print(f"Hue {hue}")
    sat=0.95
    vol=0.45
    windSat = windFactor/0.25
    windVol = windFactor/0.55
    if (mode==0):
        #set to temp.
        current_leds[index]=[hue, sat, vol]
        base_leds[index]=[hue, sat, vol]
        #no target, mode is flat
    elif (mode==2):
        #set to temp - pulse for wind effect
        current_leds[index]=[hue, sat, vol]
        base_leds[index]=[hue, sat, vol]
        target_leds[index]=[hue, sat- uniform(windSat,1)*windSat, vol + uniform(windVol,1)*windVol]
        
    else: #mode=1
        #rain blue - flash
        current_leds[index] = [randrange(0, 50), randrange(20, 100), randrange(50, 255)]
        base_leds[index] = [0, 15, 60]
        target_leds[index]= [0, 15, 60]
    
def set_array():
    if (not light):
        blank_lights()
        return
    
    # temp scaled 0-50 degrees
    temp = float(max(0.0, min(50.0, temperature)))
    #wind - our record is 65km/h
    # in m/s 0.3 = 0
    # to 1.5 light air
    # to 3.3 light breex
    # to 5.4 - gentle
    # to 7.9 Moderate breeze
    # 10.7 fresh
    # 13.8 Strong
    # 17.1 high wind
    # 20.7 Gale (our gust max)
    # 24.4 Stong gale
    windSpeed = min(20.7, wind)
    #windSpeed = max(9, wind)
    # Wiind probability is "above" (rain is "below")
    rustleLeaves = 1 - 0.5 * windSpeed / 20.7
    # Factor will set the "trob" of the LED @todo constants 0.55 max
    windFactor = max(0, windSpeed/20.7)
    #Rain mode 100mm/h = 0.1 prob max
    rainRate = min(100, rain)
    #probability of precipitation
    pop = 2*rainRate / 1000 
    for count in range(NUM_LEDS):
        switchMode=uniform(0,1)
        if (switchMode>rustleLeaves):
            #pulse
            set_colour_and_effect(2, count, temp, windFactor)
        elif (switchMode<pop):
            set_colour_and_effect(1, count, temp)
            #no traget, mode is flat
        else: #default
            set_colour_and_effect(0, count, temp)

def blank_lights():
    for i in range(NUM_LEDS):
        #led_strip.set_rgb(i,current_leds[i][0], current_leds[i][1], current_leds[i][2])
        led_strip.set_rgb(i, 0, 0, 0)
        mode_leds[i]=0
        

def set_lights():
    for i in range(NUM_LEDS):
        #led_strip.set_rgb(i,current_leds[i][0], current_leds[i][1], current_leds[i][2])
        mode = mode_leds[i]
        if (mode == 1):
            led_strip.set_rgb(i, int(current_leds[i][0]), int(current_leds[i][1]), int(current_leds[i][2]))
        else:
            led_strip.set_hsv(i, current_leds[i][0], current_leds[i][1], current_leds[i][2])

def set_weather():
    global temperature, wind
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

def status_handler(mode, status, ip):
    # reports wifi connection status
    print(mode, status, ip)
    print('Connecting to wifi...')
    # flash while connecting
    for i in range(NUM_LEDS):
        led_strip.set_rgb(i, 255, 255, 255)
        time.sleep(0.02)
    for i in range(NUM_LEDS):
        led_strip.set_rgb(i, 0, 0, 0)
    if status is not None:
        if status:
            print('Connection successful!')
        else:
            print('Connection failed!')
            # light up red if connection fails
            for i in range(NUM_LEDS):
                led_strip.set_rgb(i, 255, 0, 0)

# set up wifi
network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)
uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))

# get the first lot of data
set_weather()

timer = Timer(-1)
timer.init(period=UPDATE_INTERVAL * 1000, mode=Timer.PERIODIC, callback=lambda t: set_weather())


async def serve_client(reader, writer):
    global light
    print("Client connected")
    request_line = await reader.readline()
    print("Request:", request_line)
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass
    request = str(request_line)
    led_on = request.find('/light/on')
    led_off = request.find('/light/off')
    print( 'led on = ' + str(led_on))
    print( 'led off = ' + str(led_off))
    stateis = ""
    if led_on == 6:
        print("led on")
        light=True
        stateis = "LED is ON"

    if led_off == 6:
        print("led off")
        light=False
        stateis = "LED is OFF"
    response = "State:" + stateis
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)

    await writer.drain()
    await writer.wait_closed()
    print("Client disconnected")


async def main():
    print('Setting up webserver...')
    uasyncio.create_task(uasyncio.start_server(serve_client, "0.0.0.0", 80))
    #while True:
    #    uasyncio.gather(
    #        uasyncio.start_server(serve_client, "0.0.0.0", 80),
    #        glow()
    #        )
    while True:
        set_array()
        if (light):
            #print("heartbeat")
            #await uasyncio.sleep(5)
            for i in range(15):
                move_to_target_hsv()
                #time.sleep(1) #.003 for 25-255;
                #print(f"looped {current_leds[0][2]}")
                set_lights()
            #temperature = temperature + 1
            #await uasyncio.sleep(5)
        await uasyncio.sleep(0.001)

try:
    uasyncio.run(main())
    
finally:
    uasyncio.new_event_loop()
