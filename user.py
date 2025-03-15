from pyb import USB_VCP, UART, repl_uart

def user(shares):
    motorL = shares['motorL']
    motorR = shares['motorR']
    sensor_array = shares['sensor_array']
    #linesensor = shares['sensor_array']
    #imu = shares['imu']
    ser = USB_VCP()
    while True:
        if ser.any():
            char_in = ser.read(1).decode()
        
            if char_in == "m":
                motorL.disable()
                motorR.disable()
            elif char_in == "n":
                motorL.enable()
                motorR.enable()
            elif char_in == "c":
                start_calibration(sensor_array, motorR, motorL)
            elif char_in == "v":
                sensor_array.save_calibration()
        yield

        def start_calibration(sensor_array, motorR, motorL):
            print("Starting line sensor calibration...")
            sensor_array.calibrate(samples=500, delay_ms=10)
            print("Calibration complete.")
            return
