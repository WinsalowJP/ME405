"""
@file main.py
@brief Main entry point for the ROMI control system.

This module initializes the hardware components (sensors, motors, encoders, IMU, etc.),
loads calibration data, and sets up a task scheduler to run various control tasks
such as PID control, user control, encoder updates, and button press handling.
"""

from cotask import Task as Task
from cotask import TaskList as TaskList
import pyb
from pyb import Pin, Timer, USB_VCP, I2C, ExtInt

# Module imports
from button_press import button_task as button_task
from t4 import Track_1
from user import user
from encoder_update import encoder_update
from encoder import Encoder as Encoder
from motor import Motor as Motor
from line_sensor import LineSensorArray
from imu import BNO055

def main():
    """
    @brief Initializes hardware components and schedules control tasks.
    
    This function sets up encoders, motors, a line sensor array, and an IMU.
    It loads sensor calibration data, creates shared objects for task communication,
    and initializes a list of tasks which are then scheduled in an infinite loop.
    
    @note The infinite loop at the end continuously calls the task scheduler.
    """
    #------------sensor setup----------------------
    # Initialize left encoder and motor.
    encoderL = Encoder(3, Pin.cpu.C6, Pin.cpu.C7)
    motorL = Motor(Pin.cpu.C9, Pin.cpu.B12, Pin.cpu.A5, 2, 1)
    
    # Initialize right encoder and motor.
    encoderR = Encoder(4, Pin.cpu.B6, Pin.cpu.B7)
    motorR = Motor(Pin.cpu.A10, Pin.cpu.A7, Pin.cpu.A0, 5, 1)
    
    # Set initial motor efforts.
    motorR.set_effort(20)
    motorL.set_effort(20)

    # Setup line sensor array with designated sensor pins.
    sensor_pins = [Pin.cpu.C3, Pin.cpu.C2, Pin.cpu.B1, Pin.cpu.C5, Pin.cpu.B0, Pin.cpu.A4, Pin.cpu.A1, Pin.cpu.C4]
    sensor_array = LineSensorArray(sensor_pins)
    sensor_array.load_calibration()

    # Initialize I2C for communication with the IMU.
    i2c = pyb.I2C(3, I2C.CONTROLLER, baudrate=400000)

    # Setup IMU sensor.
    imu = BNO055(i2c, address=0x28)
    # Uncomment the following lines to calibrate or save calibration data.
    # imu.calibrate_imu()
    # imu.save_calibration_to_file(filename="IMU_Calibraion")
    imu.load_calibration_from_file(filename="IMU_Calibraion")

    flag = 0

    # Shared objects dictionary for task communication.
    shared_objects = {
        'motorL': motorL,
        'motorR': motorR,
        'sensor_array': sensor_array,
        'imu': imu,
        'encoderL': encoderL,
        'encoderR': encoderR
    }

    #----------task list--------------------------------------
    ## @brief PID Control task using Track_1.
    t4task = Task(lambda: Track_1(shared_objects), name="PID Control", priority=0, period=10, profile=True, trace=True)
    
    ## @brief User control task for processing user input.
    usertask = Task(lambda: user(shared_objects), name="User Control", priority=3, period=10, profile=True, trace=True)
    
    ## @brief Encoder update task to refresh encoder values.
    encodertask = Task(encoder_update, name="Encoder", priority=2, period=10, profile=True, trace=True, shares=shared_objects)
    
    ## @brief Button task for handling button press events.
    buttontask = Task(lambda: button_task(shared_objects, flag), name="Button Task", priority=4, period=10, profile=True, trace=True)
    
    #----------append tasks to the task list----------------
    task_list = TaskList()
    task_list.append(t4task)
    task_list.append(usertask)
    task_list.append(encodertask)
    task_list.append(buttontask)
    #---------------------------------------------------------
    while True:
        task_list.pri_sched()

if __name__ == "__main__":
    main()
