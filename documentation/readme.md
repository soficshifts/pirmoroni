# Pimoroni documentation.

- [Wireless Plasma Stick Temperature Wind and Rain.](./wireless-plasma/wireless-plasma-ecowitt-weather.md) using the Ecowitt API (or your own webserver that conforms to it).
- [Galactic Unicorn Retro Clock with Temperature, Wind, and Rain](./galacticUnicorn/galactic_unicorn_retro_weather_clock.md) using the Ecowitt API (or your own webserver that conforms to it).
- [Enviro Urban Volts to Decibels](./enviro-urban/enviro-urban-volts-to-decibels.md) describes how convert the voltage reading of your Urban to decibels (an approximation).

# Using the demo programs

## Ecowitt API

To use the wireless plasma and Galactic Unicorn, you will need to setup an Ecowitt API.  This is a rough guide - you'll need to consult the Ecowitt documentation.

### Setting up your Ecowitt API

This also works for Aercus Instruments stations that are compatible with Ecowitt.  It assumes you have setup your weather station to send data to Ecowitt.

This will be up to you.  The guide can be found on [Ecowitt's Site](https://api.ecowitt.net).  You will need to login to your account to access and setup the API.  You need 

1. An Application Key from Ecowitt.
2. An API key from Ecowitt
3. Your weather stations MAC address (should be in the Ecowitt setup screen of your station console/app when you setup your station to send data to Ecowitt).

You can also use a custom web server/URL, but your data will need to come back in Ecowitt JSON format with the appropriate units for the measurements.

**Note** I don't use the Ecowitt API anymore, so this URL and JSON may now be different.  However, the API should be stable.  Verify your parameters with the Ecowitt documentation.

You then set the URL in the scripts as:

```python
# URL to get the data from.  Data must be returned in Ecowitt format.
URL="https://api.ecowitt.net/api/v3/device/real_time?application_key=<your_application_key>&api_key=<your_api_key>&mac=<your_station_mac_address>&call_back=all&temp_unitid=1&pressure_unitid=3&wind_speed_unitid=6&rainfall_unitid=12"
```
You will need the other parameters as they return the values in the units used/calibrated by the program.

#### JSON Format

Data returned should look similar to the following.  You may have more data points (such as units), but these are the ones needed by the applications.  I chose the "feels_like" for the temperature.

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