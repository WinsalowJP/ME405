from pyb import Timer
import time

class Encoder:
    def __init__(self, tim, chA_pin, chB_pin):

        self.tim = Timer(tim, period=0xFFFF, prescaler=0)
        self.tim.channel(1, pin=chA_pin, mode=Timer.ENC_AB)
        self.tim.channel(2, pin=chB_pin, mode=Timer.ENC_AB)

        self.position = 0  # Total wheel position in ticks
        self.prev_count = self.tim.counter() # Last motor count
        self.delta = 0  # Change in count
        self.dt = 1  # Time difference (initialize to avoid div by zero)
        self.prev_time = time.ticks_us()  # Previous time in microseconds

        # Encoder scaling
        self.wheel_cpr = 1440
        # Linear motion calculation
        self.wheel_radius_mm = 36
        self.wheel_circumference_mm = 2 * 3.1416 * 36 # 2πr
        self.mm_per_tick = self.wheel_circumference_mm / self.wheel_cpr  # Distance per tick



    def update(self):
        count = self.tim.counter()
        # print(self.tim.counter())

        # Calculate delta (handling overflow)
        self.delta = count - self.prev_count  
        if self.delta > 0x7FFF:  
            self.delta -= 0x10000
        elif self.delta < -0x7FFF:  
            self.delta += 0x10000

        # Convert motor ticks to wheel ticks
        wheel_delta = self.delta *self.mm_per_tick
        self.position += wheel_delta  # Update total position in wheel ticks

        # Time tracking for velocity
        now = time.ticks_us()
        self.dt = time.ticks_diff(now, self.prev_time) / 1_000_000  # Convert to seconds
        self.prev_time = now
        self.prev_count = count


    def get_position(self):
        """ Returns the linear position in millimeters """
        return self.position

    def get_velocity(self):
        """ Returns velocity in mm/s """
        return (self.delta * self.mm_per_tick) / self.dt if self.dt > 0 else 0
    def zero(self):
        self.position = 0