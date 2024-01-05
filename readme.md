# Pirmonoi Projects

This repository contains work I've done using various Raspberry Pi 2040 devices from [Pimoroni](https://www.primoroni.com).

As a self-confessed data junkie who owns a weather station.  I discovered their gadgets and saw a challenge: how does one display data on these devices?  

So I got to it.  My weather station is an Aercus Instruments [Weathermaster](https://www.aercusinstruments.com/aercus-instruments-weathermaster-advanced-weather-station-with-wifi-and-optional-extra-sensors/) (compatible with Ecowitt).  So I can call the Ecowitt API and get the readings from my weather station.

You can choose to use the Ecowitt API, or a custom server/API that returns the Ecowitt JSON structure; or change the code to process the API data that suits your needs.

As code expects JSON data in Ecowitt format, if you own a device that sends data to Ecowitt, you can setup an Application and API key and get your data that way.

There are two code samples:

- wireless-plasma: Inspried by the weather application, this project allows you to show the temperature, wind and rain on a wireless plasma device such as [Skully](https://shop.pimoroni.com/products/wireless-plasma-kit?variant=40362173399123)
- galacticUnicorn: This is a "retro" rotary clock that displays temperature, wind and rain: the [53 x 11 model](https://shop.pimoroni.com/products/space-unicorns?variant=40842033561683).  (Documentation coming soon)

There is also a guide for [Pimoroni Enviro Urban](https://shop.pimoroni.com/products/enviro-urban?variant=40056508219475) users to convert the output of the voltage of the microphone (the "noise" parameter) to decibels.

Head over to the [Documentation](./documentation) to find out more.
