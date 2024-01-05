# Displaying Temperature, Wind, and Rain on the Wireless Plasma Stick with the Ecowitt API

This [code](../wireless-plasma/main.py) will source weather data from an Ecowitt compatible API and display:

- The temperature as a colour from blue (cold) to red (hot).
- The rain rate as random flashes of blue.  The intensity and frequency of flashes increases as the rain rate increases.
- The wind as random pulses of colour hue and saturation changes: like leaves rustling in a tree.  The intensity and frequency of the pulses increases as wind speed increases.
- It also runs a webserver (provided in the micropython firmware) to turn LEDs on or off via a simple API.

You'll need to adjust this and make changes to API calls and calibrations to better suit your needs.  This guide will assist, but assumes a knowledge of Python, JSON, and colour theory.  So its not for beginners.  And as it "works for me", I probably won't respond to bugfixes.  Its provided "as-is", but I'd welcome improvements/pull requests.

It was inspired by the [weather.py](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/plasma_stick/weather.py) provided by Pimoroni in their examples.

## Setting up your Wireless Plasma

The `main.py` program uses the standard `WIFI_CONFIG.py` provided by [Pimoroni](https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/plasma_stick).  You'll need to setup your wireless credentials plus any other applicable settings.

## Setting up your Ecowitt API

This also works for Aercus Instruments stations that are compatible with Ecowitt.  It assumes you have setup your weather station to send data to Ecowitt.

This will be up to you.  The guide can be found on [Ecowitt's Site](https://api.ecowitt.net).  You will need to login to your account to access and setup the API.  You need 

1. An Application Key from Ecowitt.
2. An API key from Ecowitt
3. Your weather stations MAC address (should be in the Ecowitt setup screen of your station console/app when you setup your station to send data to Ecowitt).

You can also use a custom web server/URL, but your data will need to come back in Ecowitt JSON format with the appropriate units for the measurements.

**Note** I don't use the Ecowitt API anymore, so this URL and JSON may now be different.  Please consult the Ecowitt documentation.

In the [main.py](../wireless-plasma/main.py) set the `URL` variable with your API and MAC information.

```python
# URL to get the data from.  Data must be returned in Ecowitt format.
URL="https://api.ecowitt.net/api/v3/device/real_time?application_key=<your_application_key>&api_key=<your_api_key>&mac=<your_station_mac_address>&call_back=all&temp_unitid=1&pressure_unitid=3&wind_speed_unitid=6&rainfall_unitid=12"
```

See the [Technical Notes](./wireless-plasma-ecowitt-weather.md#technical-notes) section regarding the `call_back=all` parameter.  You may need to tweak this to remove data points you don't need as I ran out of memory if I returned everything.

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

### JSON Format

Data returned should look similar to the following.  You may have more data points (such as units), but these are the ones needed by the Plasma.  I chose the "feels_like" for the temperature.

```json
{
  "data": {
    "outdoor": {
      "feels_like": {
        "value": "25.4"
      }
    },
    "wind": {
      "wind_speed": {
        "value": "0.7"
      }
    },
    "rainfall": {
      "rain_rate": {
        "value": "0.0"
      }
    }
  }
}
```

The full Ecowitt data response - this will vary depending on your other gadgets.  I have the indoor sensor, a PM2.5 particulate matter sensor, and a soil moisture sensor in addition the the main module (wind, rain, solar radiation, UV, temperature).  A warning was I found the Plasma ran out of memory with the full response, so may be best to scale it down via the `callback=` parameter in the `GET` request URL.

```json
{
  "time": "1704322948",
  "data": {
    "outdoor": {
      "feels_like": {
        "unit": "\u2103",
        "value": "27.4"
      },
      "temperature": {
        "unit": "\u2103",
        "value": "25.2"
      },
      "dew_point": {
        "unit": "\u2103",
        "value": "18.4"
      },
      "app_temp": {
        "unit": "\u2103",
        "value": "25.5"
      },
      "humidity": {
        "unit": "%",
        "value": "66"
      }
    },
    "indoor": {
      "temperature": {
        "unit": "\u2103",
        "value": "24.7"
      },
      "humidity": {
        "unit": "%",
        "value": "72"
      }
    },
    "solar_and_uvi": {
      "solar": {
        "unit": "W/m\u00b2",
        "value": "444.2"
      },
      "uvi": {
        "unit": "",
        "value": "4"
      }
    },
    "pressure": {
      "relative": {
        "unit": "hPa",
        "value": "995.4"
      },
      "absolute": {
        "unit": "",
        "value": "995.4"
      }
    },
    "rainfall": {
      "rain_rate": {
        "unit": "mm/h",
        "value": "0.0"
      },
      "daily": {
        "unit": "mm",
        "value": "0.0"
      },
      "event": {
        "unit": "mm",
        "value": "0.0"
      },
      "hourly": {
        "unit": "mm",
        "value": "0.0"
      },
      "weekly": {
        "unit": "mm",
        "value": "5.0"
      },
      "monthly": {
        "unit": "mm",
        "value": "3.8"
      },
      "yearly": {
        "unit": "mm",
        "value": "3.8"
      }
    },
    "wind": {
      "wind_speed": {
        "unit": "m/s",
        "value": "1.3"
      },
      "wind_gust": {
        "unit": "m/s",
        "value": "3.6"
      },
      "wind_speed_10m_avg": {
        "unit": "m/s",
        "value": "1.7"
      },
      "wind_direction": {
        "unit": "\u00ba",
        "value": "167"
      },
      "wind_direction_10m_avg": {
        "unit": "\u00ba",
        "value": "150"
      }
    },
    "soil_ch1": {
      "soilmoisture": {
        "unit": "%",
        "value": "37"
      }
    },
    "pm25_ch1": {
      "real_time_aqi": {
        "unit": "",
        "value": "20.8"
      },
      "pm25": {
        "unit": "\u00b5g/m\u00b3",
        "value": "5.0"
      },
      "24_hours_aqi": {
        "unit": "\u00b5g/m\u00b3",
        "value": "2.7"
      }
    }
  }
}
```