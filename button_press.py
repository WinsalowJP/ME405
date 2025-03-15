## @file button_press.py
#  This file implements a button interrupt and task to control motor actions.
#  It sets up an external interrupt on a button (pin C13) to toggle a global flag,
#  and a task function that responds by enabling or disabling the motors.
#


from pyb import ExtInt, Pin

## Global flag to indicate the button was pressed.
button_pressed = False

## @brief Interrupt callback for the button.
#  @param pin The pin that triggered the interrupt.
def button_callback(pin):
    global button_pressed
    button_pressed = True

# Set up the external interrupt on pin C13 (button).
button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, button_callback)

## @brief Task function to process button presses.
#  @param shared_objects A dictionary containing 'motorL' and 'motorR'.
#  @param flag A flag used to toggle motor state.
def button_task(shared_objects, flag):
    global button_pressed
    while True:
        if button_pressed:
            if flag == 1:
                flag = 0
                shared_objects['motorL'].disable()
                shared_objects['motorR'].disable()
                print("Motors disabled due to button press!")
                button_pressed = False
            elif flag == 0:
                flag = 1
                shared_objects['motorL'].enable()
                shared_objects['motorR'].enable()
                print("Motors enabled due to button press!")
                button_pressed = False
        yield
