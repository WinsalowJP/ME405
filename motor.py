## @file motor.py
#  This file provides a Motor class to control a motor using the pyboard.
#  It includes methods for setting motor effort, enabling, and disabling the motor.
#

from pyb import Pin, Timer

class Motor:
    ## @brief Class to control a motor driver.
    #  
    #  This class initializes the motor control pins for sleep (SLP), direction (DIR),
    #  and PWM. It sets up a PWM timer to adjust the motor's effort.
    def __init__(self, SLP, DIR, PWM, timer, channel):
        ## Initialize sleep control pin and put motor in sleep mode.
        self.SLP = Pin(SLP, mode=Pin.OUT_PP)
        self.SLP.low()  # Motor in sleep mode
        
        ## Initialize direction control pin and set default direction (forward).
        self.DIR = Pin(DIR, mode=Pin.OUT_PP)
        self.DIR.low()  # Forward
        
        ## Initialize PWM control pin.
        self.PWM = Pin(PWM, mode=Pin.OUT_PP)
        
        ## Configure the PWM timer at 20 kHz and create a PWM channel.
        tim = Timer(timer, freq=20000)
        self.ch = tim.channel(channel, Timer.PWM, pin=self.PWM)
        duty_cycle = 0
        self.ch.pulse_width_percent(duty_cycle)

    ## @brief Sets the motor effort based on a value between -100 and 100.
    #  @param effort An integer representing the desired effort.
    def set_effort(self, effort):
        if effort >= 0:
            self.DIR.low()
            self.ch.pulse_width_percent(effort)
        else:
            self.DIR.high()
            self.ch.pulse_width_percent(abs(effort))
        
    ## @brief Enables the motor by taking it out of sleep mode.
    def enable(self):
        self.SLP.high()
        
    ## @brief Disables the motor by setting sleep mode.
    def disable(self):
        self.SLP.low()
        
    ## @brief Returns the current direction state.
    #  @return 0 for forward, 1 for reverse.
    def getDir(self):
        return self.DIR.value()
