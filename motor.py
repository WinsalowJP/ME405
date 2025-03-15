from pyb import Pin, Timer

class Motor:
    def __init__(self,SLP,DIR,PWM,timer,channel): #'''Initializes a Motor object''' #LSLP = C9; LDIR = B12; LPWM = B10
        #SLP
        self.SLP = Pin(SLP, mode=Pin.OUT_PP)
        self.SLP.low()#Sleep!

        #DIR
        self.DIR = Pin(DIR, mode=Pin.OUT_PP)
        self.DIR.low() #Forward!

        #PWM
        self.PWM = Pin(PWM, mode=Pin.OUT_PP)
        
        #PWM Timer
        tim = Timer(timer, freq=20000)
        self.ch = tim.channel(channel, Timer.PWM, pin=self.PWM)
        duty_cycle = 0 
        self.ch.pulse_width_percent(duty_cycle)


    def set_effort(self, effort):
    #'''Sets the present effort requested from the motor based on an input value between -100 and 100'''
        if effort >= 0:
            self.DIR.low()
            self.ch.pulse_width_percent(effort)
        else:
            self.DIR.high()
            self.ch.pulse_width_percent(abs(effort))
        
    def enable(self):
    #'''Enables the motor driver by taking it out of sleep mode into brake mode'''
        self.SLP.high()
        
    def disable(self):
        self.SLP.low()
    def getDir(self):
        return self.DIR.value()

        
