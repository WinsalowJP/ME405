def encoder_update(shares):
    encoderL = shares['encoderL']
    encoderR = shares['encoderR']

    while True:
        encoderL.update()
        encoderR.update()
        yield
