## @file encoder_update.py
#  This file implements a task function to update encoder readings.
#  It retrieves left and right encoder objects from a shared dictionary and calls their update methods.


## @brief Updates both left and right encoders.
#  @param shares A dictionary with keys 'encoderL' and 'encoderR'.
def encoder_update(shares):
    encoderL = shares['encoderL']
    encoderR = shares['encoderR']
    while True:
        encoderL.update()
        encoderR.update()
        yield
