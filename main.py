## @file main.py
#  This file serves as the main entry point for the robotics control system.
#  It initializes hardware components including motors, encoders, sensors, and the IMU,
#  loads calibration data, and sets up a cooperative task scheduler.
#  The tasks include PID control (Track_1), user control, encoder updates, and button handling.
#

from cotask import Task as Task
from cotask import TaskList as TaskList
import pyb
from pyb import Pin, Timer, USB_VCP, I2C, ExtInt

# Module imports for additional tasks and hardware drivers.
from button_press import button_task as button_task
from t4 import Track_1
from user import user
from encoder_update import encoder_update
from encoder import Encoder as Encoder
from motor import Motor as Motor
from line_sensor import LineSensorArray
from imu import BNO055

## @brief Main function for system initialization and task scheduling.
def main():
    ## -------------- Sensor and actuator setup --------------
    # Initialize left encoder and motor.
    encoderL = Encoder(3, Pin.cpu.C6, Pin.cpu.C7)
    motorL = Motor(Pin.cpu.C9, Pin.cpu.B12, Pin.cpu.A5, 2, 1)
    # Initialize right encoder and motor.
    encoderR = Encoder(4, Pin.cpu.B6, Pin.cpu.B7)
    motorR = Motor(Pin.cpu.A10, Pin.cpu.A7, Pin.cpu.A0, 5, 1)
    # Set initial motor effort.
    motorR.set_effort(20)
    motorL.set_effort(20)

    # Setup line sensor array using specified sensor pins.
    sensor_pins = [Pin.cpu.C3, Pin.cpu.C2, Pin.cpu.B1, Pin.cpu.C5, Pin.cpu.B0, Pin.cpu.A4, Pin.cpu.A1, Pin.cpu.C4]
    sensor_array = LineSensorArray(sensor_pins)
    sensor_array.load_calibration()

    # Initialize I2C communication for the IMU.
    i2c = pyb.I2C(3, I2C.CONTROLLER, baudrate=400000)
    imu = BNO055(i2c, address=0x28)
    # Uncomment the following lines to calibrate or save calibration data.
    # imu.calibrate_imu()
    # imu.save_calibration_to_file(filename="IMU_Calibraion")
    imu.load_calibration_from_file(filename="IMU_Calibraion")

    ## Initialize shared objects for tasks.
    flag = 0
    shared_objects = {
        'motorL': motorL,
        'motorR': motorR,
        'sensor_array': sensor_array,
        'imu': imu,
        'encoderL': encoderL,
        'encoderR': encoderR
    }

    ## -------------- Task list setup --------------
    # Create tasks for various control functions.
    t4task = Task(lambda: Track_1(shared_objects), name="PID Control", priority=0, period=10, profile=True, trace=True)
    usertask = Task(lambda: user(shared_objects), name="User Control", priority=3, period=10, profile=True, trace=True)
    encodertask = Task(encoder_update, name="Encoder", priority=2, period=10, profile=True, trace=True, shares=shared_objects)
    buttontask = Task(lambda: button_task(shared_objects, flag), name="Button Task", priority=4, period=10, profile=True, trace=True)
    
    # Append tasks to the task list.
    task_list = TaskList()
    task_list.append(t4task)
    task_list.append(usertask)
    task_list.append(encodertask)
    task_list.append(buttontask)
    
    ## -------------- Main scheduling loop --------------
    while True:
        task_list.pri_sched()

## Entry point check.
if __name__ == "__main__":
    main()
