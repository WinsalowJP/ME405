"""
@file motor.py
@brief Module for controlling a motor using the pyboard.

This module contains the Motor class, which provides methods to initialize the motor,
set its effort, and enable or disable the motor driver.
"""

from pyb import Pin, Timer

class Motor:
    """
    @brief A class to control a motor driver on a pyboard.

    This class initializes the motor driver pins for sleep (SLP), direction (DIR),
    and PWM control. It provides methods to set the motor's effort, enable, disable,
    and retrieve the current direction.
    """

    def __init__(self, SLP, DIR, PWM, timer, channel):
        """
        @brief Initializes a Motor object.

        Sets up the motor driver pins for sleep, direction, and PWM control.
        The PWM signal is generated using a specified timer and channel.

        @param SLP The pin identifier for the sleep control.
        @param DIR The pin identifier for the direction control.
        @param PWM The pin identifier for the PWM output.
        @param timer The timer number used for PWM generation.
        @param channel The timer channel for PWM output.
        """
        # SLP - Sleep control pin: initialize and set to low (sleep mode)
        self.SLP = Pin(SLP, mode=Pin.OUT_PP)
        self.SLP.low()  # Motor driver in sleep mode

        # DIR - Direction control pin: initialize and set to low (forward)
        self.DIR = Pin(DIR, mode=Pin.OUT_PP)
        self.DIR.low()  # Set motor direction to forward

        # PWM - PWM control pin: initialize for PWM output
        self.PWM = Pin(PWM, mode=Pin.OUT_PP)
        
        # Setup PWM timer and channel for motor control.
        tim = Timer(timer, freq=20000)  # Timer configured at 20kHz frequency
        self.ch = tim.channel(channel, Timer.PWM, pin=self.PWM)
        duty_cycle = 0 
        self.ch.pulse_width_percent(duty_cycle)  # Initialize with 0% duty cycle

    def set_effort(self, effort):
        """
        @brief Sets the current effort requested from the motor.

        Adjusts the PWM duty cycle based on the input effort, which can range
        from -100 to 100. A positive value sets the motor to move in the forward
        direction, while a negative value sets it in the reverse direction.

        @param effort An integer representing the motor effort.
                      Positive for forward, negative for reverse.
        """
        if effort >= 0:
            self.DIR.low()  # Set direction to forward
            self.ch.pulse_width_percent(effort)
        else:
            self.DIR.high()  # Set direction to reverse
            self.ch.pulse_width_percent(abs(effort))
        
    def enable(self):
        """
        @brief Enables the motor driver.

        Takes the motor driver out of sleep mode, allowing the motor to operate.
        """
        self.SLP.high()
        
    def disable(self):
        """
        @brief Disables the motor driver.

        Puts the motor driver into sleep mode, effectively stopping the motor.
        """
        self.SLP.low()
        
    def getDir(self):
        """
        @brief Retrieves the current direction state of the motor.

        @return The value of the direction pin; 0 for forward, 1 for reverse.
        """
        return self.DIR.value()
