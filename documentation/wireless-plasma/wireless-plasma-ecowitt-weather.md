# Displaying Temperature, Wind, and Rain on the Wireless Plasma Stick with the Ecowitt API

This [code](../../wireless-plasma/main.py) will source weather data from an Ecowitt compatible API and display:

- The temperature as a colour from blue (cold) to red (hot).
- The rain rate as random flashes of blue.  The intensity and frequency of flashes increases as the rain rate increases.
- The wind as random pulses of colour hue and saturation changes: like leaves rustling in a tree.  The intensity and frequency of the pulses increases as wind speed increases.
- It also runs a webserver (provided in the micropython firmware) to turn LEDs on or off via a simple API.

You'll need to adjust this and make changes to API calls and calibrations to better suit your needs.  This guide will assist, but assumes a knowledge of Python, JSON, and colour theory.  So its not for beginners.  And as it "works for me", I probably won't respond to bugfixes.  Its provided "as-is", but I'd welcome improvements/pull requests.

It was inspired by the [weather.py](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/plasma_stick/weather.py) provided by Pimoroni in their examples.

## Setting up your Wireless Plasma

The `main.py` program uses the standard `WIFI_CONFIG.py` provided by [Pimoroni](https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/plasma_stick).  You'll need to setup your wireless credentials plus any other applicable settings.

If you have not setup an Ecowitt API for your weather station, here is a [rough guide](../readme.md#ecowitt-api).  This also shows the JSON format if you prefer to use a custom web server and want it to return a compatible format.  You can also change the function `def set_weather_data(data):` if you have a different JSON format you would like to use.

In the [main.py](../wireless-plasma/main.py) set the `URL` variable with your API application id, api key, and MAC information.  You will need to set the unit parameters as per the code below.

```python
# URL to get the data from.  Data must be returned in Ecowitt format.
URL="https://api.ecowitt.net/api/v3/device/real_time?application_key=<your_application_key>&api_key=<your_api_key>&mac=<your_station_mac_address>&call_back=all&temp_unitid=1&pressure_unitid=3&wind_speed_unitid=6&rainfall_unitid=12"
```

Please note I no longer use Ecowitt's API directly.  But when I did, the `call_back=all` parameter sometimes crashed the 2040 due to memory.  I may have cleaned up the leak, but if you have problems, consult the Ecowitt API to see if you can use this parameter to return only the three values you need.

As Ecowitt is a public API, you will have limits on call frequencies, so set the refresh rate to something "safe" such as 10min.

```python
# Set this to how often you'll refresh data from the API in seconds
UPDATE_INTERVAL = 600
```

If you want to use the code "as-is" leave the other parameters to return the units that the program has been calibrated on (metric), otherwise you'll need to adjust the code.  Check the [Technical Notes](./wireless-plasma-ecowitt-weather.md#technical-notes) on how its been calibrated.

## Web Server API

This code runs a mini web server allowing you to turn the lights on or off.  To use, replace `example.com` to your plamsa stick's IP address or DNS name.  Use `curl` or your browser.
```bash
#Lights on
curl http://example.com/light/on

#Lights off
curl http://example.com/light/off
```

## Technical notes

For further details on the JSON format used by the program (Ecowitt format) check out the [rough guide](../readme.md#json-format).

### Calibration

#### Temperature
**Units:** Degrees Celcius.

**Calibration:**  The temperature is calibrated to my climate, which is 0-50 degrees celcius.  Anything below or above is set to these limits.  You'll need to recalibrate the colour scale (possibly using purple if you live in Siberia or Saskatchewan and tempertures go below -40 degrees).  While coded in RGB, the Plasma can also do HSV, and "Colour temperature" will play nice with temperature.  Start at purple for the lowest it and will move through the scale to red for your highest.

If you prefer Kelvin, adjust accordingly. There is apparantly another unit of measure for temperature, but it makes little sense to most of the world.  So if you're in this minority group, convert/scale to it because you had to learn the conversion in science class.   Hint: they are the same at about -40.

#### Wind
**Units:** m/s (metres per second)

**Calibration:** Wind has been calibrated from `0` to `20.7m/s`.  

#### Rain
**Units:** mm/h (millimetres per hour)

**Calibration:** Rain is calibrated from `0` to `100mm/h`.

You can adjust the wind/rain extremes, but quite frankly, at these values the thing gets so noisy its doubtful to be noticed.

### Hacking Tips

I hope the code makes reasonable sense and those with python skills will be able to read it.  Some debug log lines are commented out.  The key function you may want to change for calibration or effects is `move_to_target_hsv()`.  Each LED has a mode (normal, flash, or pulse) and the effects are determined in there.  

Because we run a web server, we do need to run  `main()` in an asynchronous loop - this is different from most Pimoroni samples.  You can set the sleep `0.0001` or loop count (`15`) in `async def main():` to vary the effects.

Good luck.  This is free software.  I offer no support, but will take suggestions/pull requests.

