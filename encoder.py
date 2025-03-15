## @file encoder.py
#  This file provides an Encoder class to measure wheel position and velocity.
#  It uses a timer in encoder mode and computes distance and speed based on encoder ticks.
#
#  @author 
#  @date 
#  @copyright 

from pyb import Timer
import time

## @brief Class to manage an encoder.
class Encoder:
    ## @brief Initializes the encoder with a timer and two channel pins.
    #  @param tim The timer number.
    #  @param chA_pin The pin for channel A.
    #  @param chB_pin The pin for channel B.
    def __init__(self, tim, chA_pin, chB_pin):
        self.tim = Timer(tim, period=0xFFFF, prescaler=0)
        self.tim.channel(1, pin=chA_pin, mode=Timer.ENC_AB)
        self.tim.channel(2, pin=chB_pin, mode=Timer.ENC_AB)
        self.position = 0          # Total position in millimeters.
        self.prev_count = self.tim.counter()  # Previous encoder count.
        self.delta = 0             # Change in tick count.
        self.dt = 1                # Time interval in seconds.
        self.prev_time = time.ticks_us()  # Previous time in microseconds.

        ## Encoder scaling parameters.
        self.wheel_cpr = 1440      # Counts per revolution.
        self.wheel_radius_mm = 36  # Wheel radius in mm.
        self.wheel_circumference_mm = 2 * 3.1416 * self.wheel_radius_mm
        self.mm_per_tick = self.wheel_circumference_mm / self.wheel_cpr  # Distance per tick.

    ## @brief Updates the encoder reading and computes position and velocity.
    def update(self):
        count = self.tim.counter()
        self.delta = count - self.prev_count
        if self.delta > 0x7FFF:
            self.delta -= 0x10000
        elif self.delta < -0x7FFF:
            self.delta += 0x10000
        wheel_delta = self.delta * self.mm_per_tick
        self.position += wheel_delta
        now = time.ticks_us()
        self.dt = time.ticks_diff(now, self.prev_time) / 1_000_000
        self.prev_time = now
        self.prev_count = count

    ## @brief Returns the current linear position in millimeters.
    #  @return The position in mm.
    def get_position(self):
        return self.position

    ## @brief Calculates and returns the current velocity in mm/s.
    #  @return Velocity in mm/s.
    def get_velocity(self):
        return (self.delta * self.mm_per_tick) / self.dt if self.dt > 0 else 0

    ## @brief Resets the encoder position to zero.
    def zero(self):
        self.position = 0
