# Pomodoro Alarm - Version 1.3 OLED - Raspberry Pi Pico
# Chaka

from machine import Pin, I2C        # import Pin and I2C constructor classes from the machine module; Pin is used to set up Pico GPIO pins, and I2C is used to set up the I2C communication bus
from ssd1306 import SSD1306_I2C     # import the SSD1306_I2C class from the ssd1306 driver module; this class creates an OLED object so we can control the 0.96 OLED using methods like .text(), .fill(), and .show()
import time                         # import the time module for delays and timing, such as time.sleep()

# note:
# ssd1306.py = OLED driver module; sends OLED commands through the I2C communication protocol
# SSD1306_I2C = class/constructor from ssd1306.py used to create an OLED object
# main.py = main Pomodoro program; imports SSD1306_I2C, controls the OLED, reads the button, and controls the buzzer

# OLED setup
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)  # create an I2C object using I2C bus 0; SDA/data is on GP0, SCL/clock is on GP1, and the communication speed is 400 kHz
                                                    # setup the I2C communication bus (print i2c.scan() to see OLED address, usually 60 - 0x3C)

print("Scanning I2C...")
print("Devices found:", i2c.scan())

oled = SSD1306_I2C(128, 64, i2c)                   # create an OLED object for a 128x64 OLED using the I2C connection created above

# Button and buzzer setup
button = Pin(16, Pin.IN, Pin.PULL_UP)              # create a Pin object for GP18 as an input with the Pico's internal pull-up resistor enabled; used to read the button, where not pressed = 1 and pressed = 0
                                                   # setup AND use (read) the button using Pin class methods
buzzer = Pin(15, Pin.OUT)                          # create a Pin object for GP16 as an output; used to send voltage HIGH/LOW to turn the buzzer on/off
                                                   # setup AND use (output to) the buzzer using Pin class methods

# print(dir(SSD1306_I2C)) # for printing SSD1306_I2C class methods like .text() for oled objects like oled variable on line 18


# helper function to clear the OLED
def clear_oled():
    oled.fill(0)
    oled.show()


# helper function to write centered text on OLED
def center_text(text, y):
    x = (128 - len(text) * 8) // 2
    oled.text(text, x, y)


# OLED note:
# OLED has no real backlight. To turn the display "off", we clear the pixels.
# To turn it "on", we redraw the screen.


# welcome screen function that can be passed a session_count variable which it prints on 3rd line of oled to display total sessions since being on
def welcome_screen(session_count):
    oled.fill(0)
    center_text("Pomodoro Timer!", 0)
    time.sleep(0.3)
    center_text("Push to Start", 16)
    time.sleep(0.3)
    session_text = f"Sessions: {session_count}"    # session count message
    center_text(session_text, 32)
    oled.show()


# timer screen function with buzzer parameter for different style buzzers 
def timer_screen(buzzer_style):

    # initial display minutes (25) and seconds (00), wait 1 second because countdown starts at minutes (24) and seconds (59)
    oled.fill(0)
    center_text("Focus Time!", 8)
    center_text("25:00", 32)
    oled.show()
    time.sleep(1)
    
    # define next display minutes (24) and seconds (59) before starting countdown
    minutes = 24
    seconds = 59
    
    # start the countdown at minutes (24) and seconds (59) with 2 digit formatting 
    while True:
        # display updated minutes and seconds
        oled.fill(0)
        center_text("Focus Time!", 8)
        center_text(f"{minutes:02d}:{seconds:02d}", 32)
        oled.show()

        # once minutes and seconds reach 0 stop the countdown and call the buzzer function that is passed when timer function is called
        if seconds == 0 and minutes == 0:
            buzzer_style() 
            break

        # wait 1 second between decrementing seconds
        time.sleep(1)
        seconds -= 1

        # once seconds reach 0 go back to 59 and decrement minute
        if seconds < 0:
            minutes -= 1
            seconds = 59
        

# break screen function with buzzer parameter for different style buzzers
def break_screen(buzzer_style):

    # initial display minutes (5) and seconds (00), wait 1 second because countdown starts at minutes (4) and seconds (59)
    oled.fill(0)
    center_text("Break Time!", 8)
    center_text("5:00", 32)
    oled.show()
    time.sleep(1)
    
    # define next display minutes (4) and seconds (59) before starting countdown
    minutes = 4
    seconds = 59
    
    # start the countdown at minutes (4) and seconds (59) with 2 digit formatting 
    while True:
        # display updated minutes and seconds
        oled.fill(0)
        center_text("Break Time!", 8)
        center_text(f"{minutes:02d}:{seconds:02d}", 32)
        oled.show()

        # once minutes and seconds reach 0 stop the countdown and call the buzzer function that is passed when timer function is called
        if seconds == 0 and minutes == 0:
            buzzer_style() 
            break

        # wait 1 second between decrementing seconds
        time.sleep(1)
        seconds -= 1

        # once seconds reach 0 go back to 59 and decrement minute
        if seconds < 0:
            minutes -= 1
            seconds = 59


# buzzer style 1 function (time for break)
def buzzer_1():
    for i in range(10):
        buzzer.value(1)
        time.sleep(0.3)
        buzzer.value(0)
        time.sleep(0.3)


# buzzer style 2 function (time to focus)
def buzzer_2():
    for i in range(20):
        buzzer.value(1)
        time.sleep(0.1)
        buzzer.value(0)
        time.sleep(0.1)


# two different screens between the timer and breaks, waiting for button press to continue onto either the break or next session welcome/timer screens
# also added a idle timer display off after 20 seconds (same as welcome screen idle timer in main function)
def screens_between_timer_and_break(message1, message2):
    oled.fill(0)
    center_text(message1, 16)
    time.sleep(0.3)
    center_text(message2, 32)
    oled.show()

    idle_start = time.ticks_ms()           # same idle timer as in the main function for welcome screen (see below) 
    display_on = True                    

    while True:                     # idle and check for button press, if pressed stop idling + redraw next screen, if 20 seconds pass turn display off
        if button.value() == 0:
            time.sleep(0.3)         # debounce (wait after button press so it's not registered more than once)
            while button.value() == 0: # while the button is being pressed (== 0), wait 0.05 over and over (wait for the button to be released)
                time.sleep(0.05)       # and THEN break and move on to the next screen.
                                       # this prevents the button press from registering onto then next screen in case of long press
            break                      # if it stays pressed and the next screen shows that screen will register a button press

        if display_on and time.ticks_diff(time.ticks_ms(), idle_start) >= 20000:
            clear_oled()
            display_on = False

        time.sleep(0.05) # just to slow down the button checks in the in between screen otherwise pico will check millions times/s (not really needed, just avoids potential problems)


# main function that keeps track of sessions while incorporating timer_screen and break_screen for respective countdowns
# also displays welcome screen until button is pressed
# each timer_screen and break_screen countdown together is 1 session (25 minutes + 5 minutes = 30 minute sessions)
# also added display off after 20 seconds (20,000 ms) idle time to welcome screen + in between screens (timer/break doesn't have idle time, it just runs) 
def main():
    session_count = 0

    while True:
        welcome_screen(session_count) # session_count is initialized as 0 and passed into welcome_screen function which runs to show welcome screen with session count
        idle_start = time.ticks_ms()  # record the time at which welcome screen started and store in idle_start
        display_on = True             # need this otherwise time.ticks_diff will always be true and display remains off

        while button.value() == 1:    # remain idle on welcome screen while checking if button is pressed every 0.05 seconds (sleep 0.05, check, sleep 0.05, check, etc)
                                      # if 20 seconds pass and display is on turn the display off
            if display_on and time.ticks_diff(time.ticks_ms(), idle_start) >= 20000:
                clear_oled()
                display_on = False

            time.sleep(0.05) 

        else:                # if button is pressed (button.value == 0) then run the two timers (timer_screen and break_screen), as well as in between message screens
            time.sleep(0.5)  # debounce (wait after button press so that it's not registered more than once)

            timer_screen(buzzer_1)
            time.sleep(0.5)

            screens_between_timer_and_break("Focus Complete!", "Press for Break")

            break_screen(buzzer_2)
            time.sleep(0.5)

            screens_between_timer_and_break("Break Complete!", "Press Continue")

            session_count += 1


main()
