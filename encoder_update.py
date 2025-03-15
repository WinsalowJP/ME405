"""
@brief Updates the encoder readings for left and right encoders.

This function retrieves the left and right encoder objects from the shared dictionary,
calls their update methods to compute the latest position and velocity data, and yields
control to allow for cooperative multitasking.

@param shares A dictionary containing shared objects, which must include keys 'encoderL'
              and 'encoderR' representing the left and right encoder objects respectively.
"""
def encoder_update(shares):
    encoderL = shares['encoderL']
    encoderR = shares['encoderR']

    while True:
        encoderL.update()
        encoderR.update()
        yield
