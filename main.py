# Pomodoro Alarm - Version 1.2 - Raspberry Pi Pico
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
    session_text = f"Total Sessions: {session_count}"    # session count message
    lcd.putstr(f"{session_text:^20}") # f string formatting to center session count message in 20 spaces  
                                      # you could also nest as many f strings as you want but micropython doesn't support it and harder to read 

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
    minutes = 24
    seconds = 59
    
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
            seconds = 59
        
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
    minutes = 4
    seconds = 59
    
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
    lcd.clear()
    lcd.move_to(0, 1)
    lcd.putstr(f"{message1:^20}")  # center the message1 in 20 spaces using f string formatting (modern clean version), message1 is the variable
    time.sleep(0.3)
    lcd.move_to(0, 2)
    lcd.putstr("{:^20}".format(message2))  # center the message2 in 20 spaces using older .format formatting (there is also even older % formatting but don't bother), message2 is the variable
    idle_start = time.ticks_ms()           # same idle timer as in the main function for welcome screen (see below) 
    backlight_on = True                    
    while True:                     # idle and check for button press, if pressed stop idling + turn lcd on + break out of the loop to go onto next screen, if 20 seconds pass turn display off
        if button.value() == 0:
            lcd.backlight_on()  # turn the lcd on if you press the button and go on to the next break or welcome screen
            time.sleep(0.3)     # debounce: wait after button press so it's not registered more than once
                                # without debounce a single button press can look like multiple presses because the pico reads it so fast
            while button.value() == 0: # button-release loop: while the button is being pressed (== 0), wait 0.05 over and over (wait for the button to be released)
                time.sleep(0.05)       # and THEN break and move on to the next screen (when finger goes off the button)
                                       # this prevents the button press from registering onto then next screen in case of long press
            break                      # if it stays pressed and the next screen shows that screen will register a button press

        if backlight_on and time.ticks_diff(time.ticks_ms(), idle_start) >= 20000:
            lcd.backlight_off()
            backlight_on = False
        time.sleep(0.05) # just to slow down the button checks in the in between screen otherwise pico will check millions times/s (not really needed, just avoids potential problems)

# main function that keeps track of sessions while incorporating timer_screen and break_screen for respective countdowns
# also displays welcome screen until button is pressed
# each timer_screen and break_screen countdown together is 1 session (25 minutse + 5 minutes = 30 minute sessions)
# also added backlight off after 20 seconds (20,000 ms) idle time to welcome screen + in between screens (timer/break doesn't have idle time, it just runs) 
def main():
    session_count = 0
    while True:
        lcd.backlight_on()   # start the backlight before welcome screen
        lcd.clear()
        welcome_screen(session_count) # session_count is initialized as 0 and passed into welcome_screen function which runs to show welcome screen with session count
        idle_start = time.ticks_ms()  # record the time at which welcome screen started and store in idle_start
        backlight_on = True           # need this otherwise time.ticks_diff will always be true and backlight remains off
        while button.value() == 1:    # remain idle on welcome screen while checking if button is pressed every 0.05 seconds (sleep 0.05, check, sleep 0.05, check, etc)
                                      # if 20 seconds pass and backlight is on turn the backlight off
            if backlight_on and time.ticks_diff(time.ticks_ms(), idle_start) >= 20000:
                lcd.backlight_off()
                backlight_on = False
            time.sleep(0.05) 
        else:                # if button is pressed (button.value == 0) then run the two timers (timer_screen and break_screen), as well as in between message screens
            lcd.backlight_on()  # start the backlight (in case 20 seconds passed on welcome screen) before running the timers 
            time.sleep(0.5)  # debounce: wait after welcome screen button press so that it's not registered more than once
            timer_screen(buzzer_1)	# without debounce a single button press can look like multiple presses because the pico reads it so fast
            time.sleep(0.5)         # note the other 0.5 sec are not debounces (since button press doesn't happen and if it does debounce handled in screens_between_timer_and_break)
            screens_between_timer_and_break("Focus Complete!", "Press for Break")
            break_screen(buzzer_2)
            time.sleep(0.5)  
            screens_between_timer_and_break("Break Complete!", "Press to Continue")
            session_count += 1

        
main()

