## @file user.py
#  This file implements the user interface task using a USB virtual communication port.
#  It processes user commands to enable/disable motors and initiate sensor calibration.
#
#  @author James Pan & Anthony Bergout
#  @date 

from pyb import USB_VCP, UART, repl_uart

## @brief Processes user commands via USB to control motor states and sensor calibration.
#  @param shares A dictionary containing shared objects: motorL, motorR, and sensor_array.
def user(shares):
    motorL = shares['motorL']
    motorR = shares['motorR']
    sensor_array = shares['sensor_array']
    ser = USB_VCP()  # Initialize USB virtual communication port

    while True:
        # Check if any data is available from the USB interface.
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

        ## @brief Inner function to start line sensor calibration.
        #  @param sensor_array The line sensor array object.
        #  @param motorR The right motor object.
        #  @param motorL The left motor object.
        def start_calibration(sensor_array, motorR, motorL):
            print("Starting line sensor calibration...")
            sensor_array.calibrate(samples=500, delay_ms=10)
            print("Calibration complete.")
            return
