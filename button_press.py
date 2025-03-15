"""
@file button_press.py
@brief Implements a button interrupt and task for motor control.

This module sets up an external interrupt for a button (connected to pin C13) and defines
a callback function that sets a global flag when the button is pressed. The button_task function
uses this flag to enable or disable the motors based on a given flag value.
"""

from pyb import ExtInt, Pin

# Global flag to indicate the button was pressed.
button_pressed = False

def button_callback(pin):
    """
    @brief External interrupt callback function for the button.

    This function is triggered on the falling edge of the button press (pin C13). It sets
    the global flag 'button_pressed' to True, indicating that a button press event has occurred.

    @param pin The Pin object that triggered the interrupt.
    """
    global button_pressed
    # Set the flag when the button is pressed.
    button_pressed = True

# Set up the external interrupt on pin C13 (button)
button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, button_callback)

def button_task(shared_objects, flag):
    """
    @brief Task for processing button press events to control motor state.

    This generator function continuously checks if the button has been pressed. When a button
    press is detected, it toggles the provided flag and either enables or disables the motors
    based on the flag's current state. The global flag 'button_pressed' is reset after handling
    to avoid repeated actions.

    @param shared_objects A dictionary containing shared objects, including keys 'motorL'
                          and 'motorR' for the left and right motor objects.
    @param flag A flag value that determines the motor state:
                - If flag is 1, the motors are disabled.
                - If flag is 0, the motors are enabled.
    """
    global button_pressed
    while True:
        if button_pressed:
            if flag == 1:
                flag = 0
                # Disable the motors when the flag is 1 and the button is pressed.
                shared_objects['motorL'].disable()
                shared_objects['motorR'].disable()
                print("Motors disabled due to button press!")
                # Reset the flag to avoid repeated motor disabling.
                button_pressed = False
            elif flag == 0:
                flag = 1
                # Enable the motors when the flag is 0 and the button is pressed.
                shared_objects['motorL'].enable()
                shared_objects['motorR'].enable()
                print("Motors enabled due to button press!")
                # Reset the flag to avoid repeated motor enabling.
                button_pressed = False

        yield
