# brick-phone
I took a 1992 Motorola 1G brick-style cell phone, removed the insides, and rebuilt it from scratch using modern parts centered around a Pi Pico 2 microcontroller. This repo has key information about the project for those that want to learn more about it, as well as notes for myself.

[Check out the video](https://youtu.be/6bUMHgfxNoo) or see the photos below:

## Overview
I wired up 20 microswitches and arranged them in a key matrix using 30 guage relay wire. The row and columns are wired into the Pico 2. CircuitPython is used to read the switches. It also drives the color LCD via SPI to replicate the original seven segment LED display. The Pico then sends commands via I2C to two ADG729 Dual 1-to-4 Analog Matrix Switches. These switches "press" buttons on a modified bluetooth dialer/2G cell phone embedded in the case. It is all powered by a 3.7v 2200mAh lithium ion battery. The Pico code is in this repo as `code.py`. Here's a very high level diagram:

<img src="/diagram.png">

## Parts list
Raspberry Pi Pico 2

[6mm tactile button switches](https://www.adafruit.com/product/367)

[1.3" 240x240 TFT LCD Display - ST7789](https://www.adafruit.com/product/4313)

[Adafruit ADG729 Dual 1-to-4 Analog Matrix Switch](https://www.adafruit.com/product/5932)

BM10 Wireless Dialer/Mini Phone

[Lithium Ion Battery - 3.7v 2200mAh](https://www.adafruit.com/product/1781)

[PowerBoost 1000 Charger/power supply](https://www.adafruit.com/product/2465)

## The Build
To fit the project inside the brick phone case, I want with multiple PCBs stacked on top of each other, connected mostly by 30 gauge wire. See the schematic diagram pdf for the wiring of the Pico, switches, and dialer.

### Prepping the iPhone
If connecting the BM10 via Bluetooth to an iPhone, the pointers below may help in troubleshooting:

- Check Restrictions: Go to Settings > Screen Time > Content & Privacy Restrictions and ensure Bluetooth sharing is allowed.

 - If necessary, Reset Network Settings: This clears all Bluetooth, Wi-Fi, and VPN settings, which often resolves connectivity issues. Go to Settings > General > Transfer or Reset iPhone > Reset > Reset Network Settings.
