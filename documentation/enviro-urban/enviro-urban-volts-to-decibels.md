# Enviro Urban

A wireless outdoor air quality monitoring board with environmental and particulate sensors and a microphone, which records "noise".

## Converting Noise Voltage to Decibels

Please be advised I'm no audio engineer or physics expert, but I'm pretty good at math; and know a bit about electronics.  So this is a summary of how I came about getting this formula based on public information on the topic.

The formula that gives an approximation (with hopes to improve the Gain adjustment) is.

> Noise in dB = 20log(Reading / 0.0079433) + 35

There's a caveot to the formula.  Consider a 0 volt reading.  In this case the formula gives 35dB, which is obviously wrong.  This is due to a microphone's signal to noise ratio (SNR).  The [mic's datasheet](https://www.mouser.co.uk/datasheet/2/218/know_s_a0010769161_1-2271807.pdf) indicates an SNR of 59 dBA.  Based on these specs, the mic is unable to pick up sound below 35dB (94 minus 59).  

> SNR = 94dB – Self Noise
>> so if the SNR is 59, we see
>>> Self Noise = 35dB

So any result < 35dB should be interpreted as 0dB since the Mic and ciruitry generate that much natural noise.  Studio and professional microphones will have SNRs in the high 80's or low 90s, but also cost 100s if not 1000s of dollars.

If you are using an environment that only computes natural (rather than base 10) logs, for example Grafana or Prometheus, this formula leverages logs' change of base forumla to get

> Noise in dB = (20 / ln(10)) * ln(Reading / 0.0079433) + 35

Read on to understand how these numbers are derived and a bit more about the signal to noise ratio.

### The deriviation

Sound level tends to be measured in decibel units, which for sound are a logarithmic ratio to a reference pressure (sound waves travel through the air as pressure variations that our ears pick up).  There is a direct relationship between a voltage reading of a microphone and the sound pressure in dB.

There are various references used for sound, especially as humans experience different frequency sounds as "louder" than other frequencies of the same amplitude (pressure).  For the Enviro readings ([v0.10](https://github.com/pimoroni/enviro/blob/v0.0.10/enviro/boards/urban.py) of firmware), the voltage is the peak to peak difference of the highest and lowest voltage reading in a half-second sample.  Since we cannot factor in a frequency, we can only measure dB as pressure.  This is known as the "Z Filter" (Z for Zero).  It is sometimes denoted `dBZ`.  

#### General Forumla for Mic Volts to Db

The formula for dB Z from voltage V<sub>1</sub> compared to the sensitivity reference voltage V<sub>0</sub> with the standard sensitivity calibration volume S and a gain (amplification) of G (in dB) is

> dB = 20log(V<sub>1</sub> / V<sub>0</sub>) + S - G

##### Getting reference voltage, V<sub>0</sub> for our mic

We will discuss S (usually equals 94dB as standard) and G later.  First we work out what our reference voltage V<sub>0</sub> is.  This is obtained using the [mic's datasheet](https://www.mouser.co.uk/datasheet/2/218/know_s_a0010769161_1-2271807.pdf) sensitivity value.  We will use the "typical" value of `-42dB` using a 94dB 1kHz reference sound.
This value itself is in decibels, and has been calibrated to a standard reference voltage where 1 volt = 0 dB.  So using this fact, we can get the voltage the mic would generate picking up a `94 dB` sound at `1kHz` by solving:

> -42 = 20log( V<sub>1</sub> / 1)

The resultant reference voltage is V<sub>1</sub> = `0.0079433`.  

##### Determing S and Gain offset.

Basically, the mic will output a voltage of `0.0079433 V` if it picked up a 94 dB sound (technically at 1kHz, but we won't consider frequency).  Thus

> S = 94 dB

Most microphones' SNRs and Senstivity values are calibrated to a 94dB signal.  

So ignoring gain (and also frequency, as we noted above), we thus now know our formula for a voltage reading V<sub>1</sub> to be.

> dB = 20log( V<sub>1</sub> / 0.0079433) + 94

##### Gain (or amplification)

The datasheet shows the mic's voltage has been amplified via an OpAmp circuit, so we need to adjust for the amplification (aka Gain).  If the gain is in voltage, you would subtract it from your voltage reading prior to the log calculation, if it is given in dB, you would subtract it from S.

The datasheet states the gain is the ratio of two resistors `R2/R1` - these resistors would be chosen by the manufacturer (Pimoroni), and at this point, I have not obtained them.  But basically the resistance ratio is also the voltage gain ratio (via Ohm's Law I think), so if the ratio, for example was `3`, that would indicate the voltage has been amplifed by a factor of 3, so we'd divide our reading voltage by the ratio: e.g. V<sub>1</sub> = reading / 3 to get the unamplified voltage for the log. and add 94, as then Gain is no longer relevant.

In the case of the current formula, this was obtained by taking a reading of the enviro at the same time as using noise app on a smartphone.  The calculated log value in dB from the Enviro was about 35 dB too low, so this was added as the adjustment to the log ratio.  

Naturally, there are many caveots here.

- Most mic's have a frequency response, and their voltage output is not constant with frequency.  You can see the frequency response in the datasheet.  Lower and higher frequencies affect the sensitivity.
- Amplifiers can also be affected by frequency and input voltage: they may not amplify frequency consistently, or constantly amplify input voltages.
- Variations such as temperature, power to the mic, and other factors will affect the reading.  Tolerances on the op amp resistors will amplify the error tolerances on the gain.  
- Since `log(0)` is undefined, the formula does not work for the trivial case (obviously, if the voltage reading is zero, there is no sound).   In fact, due to the signal to noise ratio of `59 dBA`, this indicates that with no sound, the mic will generate voltage that would equate to `35dB`, which is about `0.1mV`.  Thus, readings of 35dB or less would have to be interpreted as `0dB`.

### About that number 35...hmmm

The `35` in the formula was obtained by comparing readings to a smartphone app decibel meter and adjusting.  But one could ask if the adjustment was as easy as taking the reference sound level of 94dB and adjusting by the SNR of 59dbB which gives 35dB.

I don't think this is normally the case, just a lucky break.  However, it is possible that the mic's amplification resistor ratio was set to produce the gain of the SNR of the mic.  This may be considered best practice for OpAmps.  

Most uses of such a microphone would to be use a variable resistor so the gain can be adjusted.

### Final notes on dB

As dB is logaritmic, it does not scale linearally to voltage.  The rules of thumb are

1. Doubling the voltage will increase volume by approximately 6dB.  Similarily, halving the voltage will reduce volume by 6dB.
2. To raise the dB by 10, you will need to increase the voltage 10 times. Thus a 20dB gain in volume is 100 times the voltage.
3. Prolonged exposure to levels above 80dB can damage hearing.  Anything over 120dB can instantly cause permanent or temporary ear damage.  Stay well away from operating jet engines.
