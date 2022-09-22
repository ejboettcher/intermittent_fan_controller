Based on 

# Intermittent Fan Controller
## By: Evelyn J. Boettcher
## Written for Anaconda's DIY 

## Background

I simply cannot sleep with a fan constantly blowing on me. My husband can not sleep without a fan on him. Initially, I
thought we'd never be able to find a happy medium, since ceiling fans are designed to be either on or off all night. I 
realized that if I could find a way to turn our fan off after five minutes and then back on after another 20 minutes, 
we’d both be able to sleep well. So, I built an adjustable, intermittent fan controller with roughly $30 worth of 
electronics and two Python scripts.


This project uses a Raspberry Pi Zero, a low-pass filter, and about 20 cm of wire to control a ceiling fan. 
In addition, a custom Python Flask application allows you to set how long the fan stays on or off. The advantage of an 
intermittent fan is that it helps prevent the room from getting stuffy, without blowing so much air that you get cold.


|                Flask App                 | Raspi Fan Controller with Cat | 
|:----------------------------------------:| :---: |
| ![Flask App](./images/fan_flask_app.png) |![cat testing](./images/cat_test.jpg) |

WARNING: It might blow your mind to realize that a general-purpose input/output (GPIO) pin, when toggled from high to 
low really fast, can create radio frequencies (RF).  These RF signals can in turn be used to power your fan without 
using its remote. Note that IT IS ILLEGAL to transmit at many frequencies. You must use a low-pass filter 
(a 433MHz low-pass filter will keep you legal).

## Setup
A Python Flask app served on the Raspberry Pi Zero will be used to configure how long the fan stays on/off and to set 
the fan’s speed. Flask is a Python web framework that enables the user to easily develop web apps with minimal setup.

Serving a Flask app is as simple as typing python app.py in a terminal. In this web app, button presses trigger 
an async command on the Raspberry Pi Zero. This command sends an on-off keying (OOK) signal at the fan’s receiving 
frequency via [rpiTX](https://github.com/F5OEO/rpitx), which turns a GPIO pin 7 (BCM 4) on/off. This process of turning the GPIO pin on/off is what generates 
the RF signal. The 20 cm of wire acts as an antenna, so the signal can reach the fan’s receiver.


### Figuring out the RF commands

The OOK signal is transmitted at a main frequency. You must figure out the frequency at which the fan’s remote controller 
transmits, and how that OOK signal is encoded. The two main ways to figure out what frequency a remote uses is to 
either measure it or read the manual. A cheap way to measure it is to use a USB TV tuner as demonstrated in the 
[Hack My Ceiling Fan Radio Signal with a $15 USB TV Tuner](https://www.youtube.com/watch?v=_GCpqory3kc&list=PLd0h4lJ7ve9KpkbUbsEXxsDlqNxwA-aWH&index=1)
YouTube video. Or, you can refer to the FCC website. 
All transmitters have to report what frequency they use. Mine uses 304MHz (FCC ID: KUJCE1000)—I measured 304.2MHz, 
which is close enough. There is variation from remote to remote; I have three Minka Aire remotes, and some operate 
at a higher or lower frequency than stated on the FCC site [FCC ID: KUJCE10007](https://fccid.io/KUJCE10007). 



![fan remote back](./images/remote_back.jpg)

To figure out how the RF signal is encoded, you can measure it with a USB TV tuner (see below) or refer to this 
[River's Educational Video](https://www.youtube.com/watch?v=3lGU7PjJM7k)) YouTube video. 
The table below lists the OOK codes for Minka Aire fans.


### Fans Codes

| Action       | Code  | 
|:-------      | :-----|
| Light: On    | 01010 | 
| Light: Off   | 10010 |
| Fan: Low     | 00100 |
| Fan: Med     | 01000 |
| Fan: High    | 10000 |
| Fan: OFF     | 10100 |
| Fan: Reverse | 00010 |

### Fan Unique ID Key
Most remotes have toggle switches on the back, near the battery. The Minka Aire has two sets of four toggle switches 
(eight digits) that are used to set its unique ID, where Up = 1 and Down = 0.

Where:
Up  == 1
Down == 0

## Putting it all Together
### Parts

* [433 Low Pass Filter](https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2334524.m570.l1313&_nkw=433MHz+low+pass+filter&_sacat=0&LH_TitleDesc=0&_sop=15&_osacat=0&_odkw=400+MHz+low+pass+filter&LH_BIN=1&mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5338762671&customid=minkaaire2&toolid=20012&mkevt=1)
 ~ $ 5.50
* ~20 cm of wire
* Raspberry Pi Zero ~ $25
* SD Card: $10

Nice to have:
* [USB TV Tuner](https://www.amazon.com/MyGica-Antenna-Laptop-Windows-Android/dp/B08Z383Y11/ref=sr_1_4?gclid=CjwKCAjw6MKXBhA5EiwANWLODOecn20Ud-zR47MALg8STVqo0nmHOg058T46ysVqpkDLkJTay6GUPhoCTqIQAvD_BwE&hvadid=174226871964&hvdev=c&hvlocphy=9015834&hvnetw=g&hvqmt=e&hvrand=12844467220829786195&hvtargid=kwd-4034224185&hydadcr=19108_9441150&keywords=usb+tv+tuner+stick&qid=1659979571&sr=8-4) ~ $30.00


### Software Configurations for the Raspberry Pi Zero

* Download this repo onto your raspberry pi
* Download [rpiTX](https://github.com/F5OEO/rpitx) and place it in the `./src` folder.
* You will need to configure the raspberry pi activate it's GPIO pins.
* Connect your raspberry pi to your Wi-Fi network.
  * To find the IP address, type in bash terminal: `hostname -I`.
* `python3 pip install flask, RPi.GPIO`
* Set the Fan ID in the FanRemote class located in fan_controller.py
  * This is two sets of 4 bits.

### Hardware Configuration

* Solder ~20 cm of wire to one end of 433MHz low pass filter.  
* Solder two jumper cables to the other end: one the signal line 
and the other one to ground.
* Connect the signal line to GPIO pin 7 and the ground to Raspberry Pi's ground.

### Run the Flask App

The Flask app has three main parts: app.py, index.html, and fan.css. The app.py file is the Python script that serves 
the Flask app and responds when a user presses a button in the web app. The web app consists of index.html and fan.css 
files. The fan.css file makes the app look pretty and was modeled after the css file in 
[ESP32_IR Remote repository](https://github.com/e-tinkers/esp32_ir_remote).

To run the app, go to the ./src folder and type in a terminal:


```bash
python3 app/app.py
```

This will initialize a flask app at the raspberry pi's ip address on port 5000.
Mine was at `http://192.168.2.80:5000`

The Flask app imports a fan class into the application. When a user presses a button in the app, the `main` method in 
the Flask app figures out how to respond and sends an async command to the fan.

## Warnings

**WARNING** 

**IT IS ILLEGAL** to transmit at many frequencies.  
You must use a low pass filter (433MHz Low Pass Filter will keep you legal).

## Bonus Material
### Measuring the RF Command

Using the USB TV tuner and Universal Radio Hacker (URH) software, I was able to capture the raw RF signal. 
The fan uses OOK and each bit is sent as 100 or 101:  1 = 101 and 0 = 100. The fan is expecting a signal at 304MHz, 
where the first eight bits are the fan’s ID and the next five are the fan remote command. 

* If you do want to play with a USB TV tuner and URH software, I recommend creating a conda environment and 
installing the URH within it. I also recommend installing miniconda on the Raspberry Pi Zero since it has a small processor.

By recording the signal when each button is pressed on the fan’s remote, you can then analyze each signal.
This will enable you to build out a Fan Codes table such as the one above. Note that different remotes may 
use different frequencies and encodings. 


| RF Interpretation                                           | RF Analysis |
|:------------------------------------------------------------|:---|
| ![RF Interpretation](./images/urh_signalInterpretation.png) |![RF Command](./images/minka_airUHR.png) | 


There you have it! You can create your own custom-defined remote controller using a Raspberry Pi Zero, some Python code, 
and a bit of wire. Note that if you are new to working with hardware and RF there can be a steep learning curve. 
Don’t worry if you can’t get the project to work the first or even the hundredth time; these things take practice.


### Keep Fan On

To keep the fan on, set the Fan off time to zero.

## References

Do watch River's Educational Channel for how to set up your Raspberry Pi and for the reason why we need a low pass filter.

* [Hack My Ceiling Fan Radio Signal with a $15 USB TV Tuner](https://www.youtube.com/watch?v=_GCpqory3kc&list=PLd0h4lJ7ve9KpkbUbsEXxsDlqNxwA-aWH&index=1) by River's Educational Channel.

* [Abusing Raspberry Pi GPIO pins as a radio transmitter to control my ceiling fan](https://www.youtube.com/watch?v=3lGU7PjJM7k)
	

* [ESP32_IR Remote for their wonderful css](https://github.com/e-tinkers/esp32_ir_remote)

* [FCCID KUJCE10007](https://fccid.io/KUJCE10007)

Additional Libraries

* [rpiTX](https://github.com/F5OEO/rpitx) 
