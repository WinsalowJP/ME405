"""
@file user.py
@brief Handles user interactions via USB for motor and sensor calibration control.

This module provides a user interface function that listens for commands from a USB virtual 
communication port. Based on the input, it enables/disables motors or starts the calibration 
process for the line sensor array.
"""

from pyb import USB_VCP, UART, repl_uart

def user(shares):
    """
    @brief Processes user commands from the USB virtual communication port.

    This function retrieves motor and sensor objects from the shared dictionary and continuously 
    monitors the USB_VCP interface for incoming characters. Depending on the character received, 
    it performs one of the following actions:
    - "m": Disables both motors.
    - "n": Enables both motors.
    - "c": Initiates sensor calibration.
    - "v": Saves the sensor calibration data.

    The function is implemented as a generator that yields control after each loop iteration, 
    which is useful for cooperative multitasking.

    @param shares A dictionary containing shared objects including motorL, motorR, and sensor_array.
    """
    motorL = shares['motorL']
    motorR = shares['motorR']
    sensor_array = shares['sensor_array']
    ser = USB_VCP()  # Initialize USB virtual communication port

    while True:
        # Check if any data is available on the USB port
        if ser.any():
            char_in = ser.read(1).decode()
        
            if char_in == "m":
                motorL.disable()
                motorR.disable()
            elif char_in == "n":
                motorL.enable()
                motorR.enable()
            elif char_in == "c":
                start_calibration(sensor_array)
            elif char_in == "v":
                sensor_array.save_calibration()
        yield

        def start_calibration(sensor_array):
            """
            @brief Calibrates the line sensor array.

            This inner function prints a message indicating the start of calibration, performs the 
            calibration process by taking 500 samples with a 10 ms delay between each, and then 
            prints a completion message.

            @param sensor_array The line sensor array object to be calibrated.
            """
            print("Starting line sensor calibration...")
            sensor_array.calibrate(samples=500, delay_ms=10)
            print("Calibration complete.")
            return
