"""
@file encoder.py
@brief Provides an interface for reading and processing encoder data.

This module defines the Encoder class, which is used to interface with an encoder
using a timer and two channels (for quadrature decoding). It calculates position,
velocity, and handles encoder overflow.
"""

from pyb import Timer
import time

class Encoder:
    """
    @brief Class to manage an encoder for measuring wheel position and velocity.

    This class initializes a timer for quadrature decoding of an encoder, and computes
    the linear position (in millimeters) and velocity (in mm/s) based on the encoder ticks.
    It handles counter overflow and scales the tick counts to physical distance using the wheel
    parameters.
    """
    
    def __init__(self, tim, chA_pin, chB_pin):
        """
        @brief Initializes the Encoder object with a specified timer and pins for channels A and B.

        Configures the timer for encoder mode, sets up initial position and timing,
        and defines scaling parameters based on the wheel's properties.

        @param tim The timer number to be used for the encoder.
        @param chA_pin The pin used for encoder channel A.
        @param chB_pin The pin used for encoder channel B.
        """
        # Configure timer for quadrature encoder mode
        self.tim = Timer(tim, period=0xFFFF, prescaler=0)
        self.tim.channel(1, pin=chA_pin, mode=Timer.ENC_AB)
        self.tim.channel(2, pin=chB_pin, mode=Timer.ENC_AB)

        self.position = 0  # Total wheel position in millimeters
        self.prev_count = self.tim.counter()  # Last motor count
        self.delta = 0  # Change in count since last update
        self.dt = 1  # Time difference in seconds (initialized to avoid division by zero)
        self.prev_time = time.ticks_us()  # Previous time in microseconds

        # Encoder and wheel scaling parameters
        self.wheel_cpr = 1440  # Counts per revolution
        self.wheel_radius_mm = 36  # Wheel radius in millimeters
        self.wheel_circumference_mm = 2 * 3.1416 * self.wheel_radius_mm  # Circumference in mm (2πr)
        self.mm_per_tick = self.wheel_circumference_mm / self.wheel_cpr  # Linear distance per encoder tick

    def update(self):
        """
        @brief Updates the encoder position and calculates the time difference.

        Reads the current counter value from the timer, computes the change in ticks
        (handling potential overflow), converts the tick difference to a linear distance,
        and updates the cumulative position. Also updates the time difference used for velocity calculation.
        """
        count = self.tim.counter()

        # Calculate delta with overflow handling
        self.delta = count - self.prev_count  
        if self.delta > 0x7FFF:  
            self.delta -= 0x10000
        elif self.delta < -0x7FFF:  
            self.delta += 0x10000

        # Convert encoder ticks to linear distance and update position
        wheel_delta = self.delta * self.mm_per_tick
        self.position += wheel_delta

        # Update timing information for velocity calculation
        now = time.ticks_us()
        self.dt = time.ticks_diff(now, self.prev_time) / 1_000_000  # Convert microseconds to seconds
        self.prev_time = now
        self.prev_count = count

    def get_position(self):
        """
        @brief Retrieves the current linear position measured by the encoder.

        @return The total position in millimeters.
        """
        return self.position

    def get_velocity(self):
        """
        @brief Calculates and retrieves the current velocity of the wheel.

        Velocity is computed based on the difference in encoder ticks and the elapsed time.

        @return The velocity in millimeters per second (mm/s). Returns 0 if the time difference is zero.
        """
        return (self.delta * self.mm_per_tick) / self.dt if self.dt > 0 else 0

    def zero(self):
        """
        @brief Resets the cumulative encoder position to zero.
        """
        self.position = 0
