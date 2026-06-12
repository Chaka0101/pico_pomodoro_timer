# Pomodoro Alarm - Version 1.1 - Raspberry Pi Pico
# Chaka

from machine import Pin, I2C        # import Pin and I2C constructor classes from the machine module; Pin is used to set up Pico GPIO pins, and I2C is used to set up the I2C communication bus
from pico_i2c_lcd import I2cLcd     # import the I2cLcd class from the pico_i2c_lcd driver module; this class creates an LCD object so we can control the 20x4 LCD using methods like .putstr(), .clear(), and .move_to()
import time                         # import the time module for delays and timing, such as time.sleep()

# note:
# lcd_api.py = base LCD API module; contains general LCD rules, functions, and classes
# pico_i2c_lcd.py = I2C-specific LCD driver module; uses lcd_api.py and sends LCD commands through the I2C communication protocol
# I2cLcd = class/constructor from pico_i2c_lcd.py used to create an LCD object
# main.py = main Pomodoro program; imports I2cLcd, controls the LCD, reads the button, and controls the buzzer

# LCD setup
i2c = I2C(0, sda=Pin(12), scl=Pin(13), freq=400000)  # create an I2C object using I2C bus 0; SDA/data is on GP12, SCL/clock is on GP13, and the communication speed is 400 kHz
                                                         # setup the I2C communication bus (print i2c.scan() to see address 39 - 0x27)
lcd = I2cLcd(i2c, 0x27, 4, 20)                       # create an LCD object for a 20x4 LCD at I2C address 0x27, using the I2C connection created above
                                                         # use (output to) LCD with I2cLcd class methods like .putstr()

# Button and buzzer setup
button = Pin(18, Pin.IN, Pin.PULL_UP)                # create a Pin object for GP18 as an input with the Pico's internal pull-up resistor enabled; used to read the button, where not pressed = 1 and pressed = 0
                                                         # setup AND use (read) the button using Pin class methods
buzzer = Pin(16, Pin.OUT)                            # create a Pin object for GP16 as an output; used to send voltage HIGH/LOW to turn the buzzer on/off
                                                         # setup AND use (output to) the buzzer using Pin class methods

# print(dir(I2cLcd)) # for printing I2cLcd class methods like .putstr() for lcd objects like lcd variable on line 17


# welcome screen function that can be passed a session_count variable which it prints on 3rd line of lcd to display total sessions since being on
def welcome_screen(session_count):
    lcd.putstr(f"Welcome to Pomodoro!")
    lcd.move_to(0, 1)
    time.sleep(0.3)
    lcd.putstr(f"Push Button to Start")
    time.sleep(0.3)
    lcd.move_to(0, 2)
    lcd.putstr(f"Total Sessions: {session_count}")

# timer screen function with buzzer parameter for different style buzzers 
def timer_screen(buzzer_style):

    # initial display minutes (25) and seconds (00), wait 1 second because countdown starts at minutes (24) and seconds (59)
    lcd.clear()
    lcd.move_to(5, 1)
    lcd.putstr(f"Focus Time!")
    time.sleep(0.3)
    lcd.move_to(8, 2)
    lcd.putstr(f"25:00")
    time.sleep(1)
    
    # define next display minutes (24) and seconds (59) before starting countdown
    minutes = 2
    seconds = 2
    
    # start the countdown  at minutes (24) and seconds (59) with 2 digit formatting 
    while True:
        # display updated minutes and seconds
        lcd.move_to(8, 2)
        lcd.putstr(f"{minutes:02d}:{seconds:02d}")
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
            seconds = 2
        
# break screen function with buzzer parameter for differnt style buzzers
def break_screen(buzzer_style):

    # initial display minutes (5) and seconds (00), wait 1 second because countdown starts at minutes (4) and seconds (59)
    lcd.clear()
    lcd.move_to(5, 1)
    lcd.putstr(f"Break Time!")
    time.sleep(0.3)
    lcd.move_to(8, 2)
    lcd.putstr(f"5:00")
    time.sleep(1)
    
    # define next display minutes (4) and seconds (59) before starting countdown
    minutes = 2
    seconds = 2
    
    # start the countdown  at minutes (4) and seconds (59) with 2 digit formatting 
    while True:
        # display updated minutes and seconds
        lcd.move_to(8, 2)
        lcd.putstr(f"{minutes:02d}:{seconds:02d}")
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
            seconds = 2

# buzzer style 1 function (time for break)
def buzzer_1():
    for i in range(10):
        buzzer.value(1)
        time.sleep(0.3)
        buzzer.value(0)
        time.sleep(0.3)

# buzzer style 2 function (time to focus)
def buzzer_2():
    for i in range(10):
        buzzer.value(1)
        time.sleep(0.1)
        buzzer.value(0)
        time.sleep(0.1)

# main function that keeps track of sessions while incorporating timer_screen and break_screen for respective countdowns
# also displays welcome screen until button is pressed
# each timer_screen and break_screen countdown together is 1 session (25 minutse + 5 minutes = 30 minute sessions)
def main():
    session_count = 0
    while True:
        lcd.clear()
        welcome_screen(session_count) # session_count is initialized as 0 and passed into welcome_screen function to be displayed on 3rd line indicating how many sessions have happened
        while button.value() == 1:
            time.sleep(0.05) # keep checking if button is pressed every 0.05 seconds
        else:                # if button is pressed (button.value == 0) then run the two timers (timer_screen and break_screen)
            time.sleep(0.5)  # debounce (wait after button press so that it's not registered more than once)
            timer_screen(buzzer_1)
            time.sleep(0.5)
            break_screen(buzzer_2)
            time.sleep(0.5)
            session_count += 1

        
main()

