from pyb import ExtInt, Pin

# Global flag to indicate the button was pressed
button_pressed = False

def button_callback(pin):
    global button_pressed
    # Set the flag when the button is pressed
    button_pressed = True

# Set up the external interrupt on pin C13 (button)
button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, button_callback)

def button_task(shared_objects, flag):
    global button_pressed
    while True:
        if button_pressed:
            if flag == 1:
                flag = 0
                # Disable the motors when the button is pressed
                shared_objects['motorL'].disable()
                shared_objects['motorR'].disable()
                print("Motors disabled due to button press!")
                # Reset the flag so the task doesn't keep disabling motors repeatedly
                button_pressed = False
            elif flag == 0:
                flag = 1
                shared_objects['motorL'].enable()
                shared_objects['motorR'].enable()
                print("Motors disabled due to button press!")
                # Reset the flag so the task doesn't keep disabling motors repeatedly
                button_pressed = False

        yield
