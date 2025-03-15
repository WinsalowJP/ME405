from cotask import Task as Task
from cotask import TaskList as TaskList
import pyb
from pyb import Pin, Timer, USB_VCP, I2C, ExtInt
#///////////////////////////////////////////////////////////////
from button_press import button_task as button_task
from t4 import Track_1
from user import user
from encoder_update import encoder_update
#module imports
from encoder import Encoder as Encoder
from motor import Motor as Motor

from line_sensor import LineSensorArray
from imu import BNO055


def main():
    #------------sensor setup----------------------
    encoderL = Encoder(3, Pin.cpu.C6, Pin.cpu.C7)
    motorL = Motor(Pin.cpu.C9, Pin.cpu.B12, Pin.cpu.A5, 2, 1)
    encoderR = Encoder(4, Pin.cpu.B6, Pin.cpu.B7)
    motorR = Motor(Pin.cpu.A10, Pin.cpu.A7, Pin.cpu.A0, 5, 1)
    motorR.set_effort(20)
    motorL.set_effort(20)

    sensor_pins = [Pin.cpu.C3, Pin.cpu.C2, Pin.cpu.B1, Pin.cpu.C5, Pin.cpu.B0, Pin.cpu.A4, Pin.cpu.A1, Pin.cpu.C4]
    sensor_array = LineSensorArray(sensor_pins)
    sensor_array.load_calibration()

    i2c = pyb.I2C(3, I2C.CONTROLLER, baudrate=400000)

    imu = BNO055(i2c, address=0x28)
    #imu.calibrate_imu()
    #imu.save_calibration_to_file(filename="IMU_Calibraion")
    imu.load_calibration_from_file(filename="IMU_Calibraion")

    flag = 0

    shared_objects = {
        'motorL': motorL,
        'motorR': motorR,
        'sensor_array': sensor_array,
        'imu': imu,
        'encoderL': encoderL,
        'encoderR': encoderR
    }

    #----------task list--------------------------------------
    t4task = Task(lambda: Track_1(shared_objects), name="PID Control", priority=0, period=10, profile=True, trace=True)
    usertask = Task(lambda: user(shared_objects), name="User Control", priority=3, period=10, profile=True, trace=True)
    encodertask = Task(encoder_update, name="Encoder", priority=2, period=10, profile=True, trace=True, shares = shared_objects)
    buttontask = Task(lambda: button_task(shared_objects, flag), name="Button Task", priority=4, period=10, profile=True, trace=True)
    #----------append to task list---------------------------
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


    
