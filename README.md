# Pico Pomodoro Timer

A very basic Raspberry Pi Pico Pomodoro timer using a 20x4 I2C LCD, button, and buzzer.

## Current Version
Version 1.2

## Features
- 25-minute focus timer
- 5-minute break timer
- Button-controlled start/continue
- Buzzer alerts
- Session count since power-on
- 20-second idle backlight shutoff on welcome/waiting screens

## Hardware
- Raspberry Pi Pico                   (RP2040 aka Pico 1 is more than enough) 
- 20x4 I2C LCD with I2C backpack      (Standard I2C 20x4 LCD from AliExpress with I2C backpack for I2C communication protocol)
- Push button                         (Any typical electronics button will do)
- Active buzzer                       (Standard electronics buzzer from AliExpress)
- 5V USB power                        (Plugs directly into Pico for 5V power)

## Important Notes
- For the code to work you need both:
  - lcd_api.py a general API library for code to communicate with LCD and display text/position text (not just I2C LCD's)
  - pico_i2c_lcd.py driver library for I2C communication protocol between pico and LCD display (technically between pico and the I2C backpack, which then controls LCD)
