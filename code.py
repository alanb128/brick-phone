# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
1G mobile phone reanimator
"""

import board
import busio
import displayio
import digitalio
import terminalio
import keypad
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from fourwire import FourWire
import pwmio
import array
import math
import time
from adafruit_st7789 import ST7789
import adafruit_adg72x

# define buttons
buttons = {
    0: ('3', 'number'),
    1: ('6', 'number'),
    2: ('9', 'number'),
    3: ('#', 'number'),
    4: ('SND', 'function'),
    6: ('VOL', 'direct'),
    7: ('2', 'number'),
    8: ('5', 'number'),
    9: ('8', 'number'),
    10: ('0', 'number'),
    11: ('CLR', 'function'),
    12: ('FCN', 'function'),
    13: ('LOCK', 'function'),
    14: ('1', 'number'),
    15: ('4', 'number'),
    16: ('7', 'number'),
    17: ('*', 'number'),
    18: ('RCL', 'function'),
    19: ('STO', 'function'),
    20: ('PWR', 'direct'),
    
    
}

# Define DTMF frequencies (in Hz)
frequencies = {
    '1': (697, 1209),
    '2': (697, 1336),
    '3': (697, 1477),
    'A': (697, 1633),
    '4': (770, 1209),
    '5': (770, 1336),
    '6': (770, 1477),
    'B': (770, 1633),
    '7': (852, 1209),
    '8': (852, 1336),
    '9': (852, 1477),
    'C': (852, 1633),
    '*:': (941, 1209),
    '0': (941, 1336),
    '#': (941, 1477),
    'D': (941, 1633),
}

# define dialer buttons for ADG:
# format: 'btn name': (ADG 1 or 2, channel)
dialer = {
    'SEL': (1, 0),
    'DIAL': (1, 1),
    '1': (1, 2),
    '2': (2, 0),
    '3': (2, 4),
    '4': (1, 4),
    '5': (2, 1),
    '6': (2, 5),
    '7': (1, 5),
    '8': (2, 2),
    '9': (2, 6),
    '0': (2, 3),
    '*': (1, 6),
    '#': (2, 7),

}


# define recall numbers:
stored = ["8338255357", "6092616600", "7012233700"]
recall_count = 0
led_timer = 33000
pair_code = "1234"

def play_dtmf(key):
    if key in frequencies:
        freq1, freq2 = frequencies[key]
        
        # Set up PWM for the first frequency
        pwm1 = pwmio.PWMOut(board.GP20, frequency=freq1, duty_cycle=32768)  # 50% duty cycle
        # Set up PWM for the second frequency
        pwm2 = pwmio.PWMOut(board.GP19, frequency=freq2, duty_cycle=32768)  # 50% duty cycle
        
        time.sleep(0.4)  # Play tone for 0.4 seconds
        
        # Turn off PWM
        pwm1.deinit()
        pwm2.deinit()


def sine_wave(freq):
    # Generate one period of sine wav.
    # Not currently used.
    length = 8000 // 440
    sine_wave = array.array("H", [0] * length)
    for i in range(length):
        sine_wave[i] = int(math.sin(math.pi * 2 * i / length) * (2 ** 15) + 2 ** 15)

    pwm = pwmio.PWMOut(board.GP19, duty_cycle=2 ** 15, frequency=440, variable_frequency=True)
    time.sleep(0.2)
    pwm.frequency = 880
    time.sleep(0.1)

def dial_number(dial_num, skip_sel=False):
    
    if not switchable:
        return
    
    time.sleep(0.20)
    for char in dial_num:
        if char in dialer and switchable:
            my_switch, my_channel = dialer[char]
            print("dialing {}.".format(char))
            if my_switch == 1:
                switch.channel = my_channel
                time.sleep(0.25)
                switch.channels_off()
                time.sleep(0.25)
            else:
                switch2.channel = my_channel
                time.sleep(0.25)
                switch2.channels_off()
                time.sleep(0.25)
        else:
            print("requested dial digit not defined.")
    if not skip_sel:
        # numbers dialed, now hit "dial" and "sel" on dialer
        print("dialing 'dial'")
        switch.channel = 1
        time.sleep(0.25)
        switch.channels_off()
        time.sleep(0.25)
        print("dialing 'sel'")
        switch.channel = 0
        time.sleep(0.25)
    
    switch.channels_off()
    
def key_event(button):
    global display_text
    global recall_count
    global led_timer
    
    
    led_timer = 53000
    
    if display_text == initial_text:
        display_text = ""
        
    if button in buttons:
        button_name, button_function = buttons[button]
        print(button_name, button_function)
        # If a number, add it to the queue
        if button_function == "number":
            if button_name != "#" and button_name != "*":
                display_text = display_text + button_name
            play_dtmf(str(button_name))
        elif button_function == "direct":
            if button in dialer and switchable:
                print("dialing {}".format(button))
                my_switch, my_channel = dialer[button]
                if my_switch == 1:
                    switch.channel = my_channel
                    time.sleep(0.25)
                    switch.channels_off()
                    time.sleep(0.25)
                else:
                    switch2.channel = my_channel
                    time.sleep(0.25)
                    switch2.channels_off()
                    time.sleep(0.25)
            else:
                print("requested direct button not defined.")
        elif button_function == "function":
            if button_name == "RCL": # load/display next stored number
                display_text = stored[recall_count]
                recall_count = recall_count + 1
                if recall_count > len(stored) - 1:
                    recall_count = 0
                pass
            elif button_name == "CLR": # clear the queue
                display_text = ""
                # clear the inuse block
                sprite_inuse.hidden = True
            elif button_name == "SND": # dial on the dialer via the ADGs
                # change the display block
                sprite_inuse.hidden = False
                dial_number(display_text)
            elif button_name == "STO": # send 1234 to dialer for pairig code
                dial_number(pair_code, True)
            elif button_name == "FCN": # send all digits to dialer to test
                dial_number('1234567890', True)
                
        else:
            print("Button defined but no action set.")
        text_area.text = display_text[-7:]   
    
    
    
    
    
    # If send, dial the number on the dialer
    
    # If a dialer key, send it along
    else:
        print("Undefined button pressed!")


# First set some parameters used for shapes and text
BORDER = 20
FONTSCALE = 2
BACKGROUND_COLOR = 0x000000  # Bright Green
FOREGROUND_COLOR = 0xFFFF00  # Yel
TEXT_COLOR = 0x00FF00

backlight_timer = 0
initial_text = "8888888"
display_text = initial_text
switchable = True

# Release any resources currently in use for the displays
displayio.release_displays()

#spi = board.SPI()
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11) #, MISO=board.GP16)
tft_cs = board.GP12
tft_dc = board.GP13

try:
    display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.GP15)
except:
    print("Could not set up display...")

display = ST7789(display_bus, rotation=270, width=240, height=135, rowstart=40, colstart=53)
print("Setting display")
# Make the display context
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = BACKGROUND_COLOR

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(50, 20, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = FOREGROUND_COLOR
sprite_inuse = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=60, y=15)
splash.append(sprite_inuse)
sprite_nosvc = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=120, y=15)
splash.append(sprite_nosvc)
sprite_roam = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=180, y=15)
splash.append(sprite_roam)

# Draw a label
# https://github.com/CedarGroveStudios/SevenSeg_font
font = bitmap_font.load_font("/SevenSeg-6.bdf")
text_area = label.Label(font, text=display_text, color=TEXT_COLOR)
#text_width = text_area.bounding_box[2] * FONTSCALE
text_group = displayio.Group(scale=6,x=10,y=100)
#    scale=FONTSCALE,
 #   x=display.width // 2 - text_width // 2,
 #   y=display.height // 2,
#
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

# Define GPIO
leds = digitalio.DigitalInOut(board.GP9)
leds.direction = digitalio.Direction.OUTPUT
leds.value = 0


# was row_pins=(board.GP16, board.GP17, board.GP18),
km = keypad.KeyMatrix(
    row_pins=(board.GP18, board.GP17, board.GP16),
    column_pins=(board.GP6, board.GP7, board.GP8, board.GP28, board.GP27, board.GP26, board.GP22),
    columns_to_anodes=True,
)

# Define I2C for using ADG729 switches
try:
    i2c = busio.I2C(scl=board.GP5, sda=board.GP4)
except:
    print("No i2c found!")
try:
    switch = adafruit_adg72x.ADG72x(i2c, 0x44)
except:
    print("switch 1 not found.")
    switchable = False
try:
    switch2 = adafruit_adg72x.ADG72x(i2c, 0x45)
except:
    print("switch 2 not found.")
    switchable = False
    
# Example usage
play_dtmf('A')  # Play DTMF tone for key 'A'

time.sleep(1)

#sprite_roam.hidden = True
sprite_nosvc.hidden = True
sprite_inuse.hidden = True
text_area.text = "-------"

while True:
    event = km.events.get()
    
    if event:
        print("event: {}".format(event))
        print("key event: {};{};{}".format(event.key_number,event.pressed, event.released))
        #print(type(event.key_number))
        if event.pressed:
            key_event(event.key_number)
    if led_timer > 0:
        if leds.value == 0:
            leds.value = 1
        led_timer = led_timer - 1
        if led_timer == 0:
            leds.value = 0
            
        
