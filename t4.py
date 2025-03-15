## @file t4.py
#  This file implements the autonomous tracking and navigation task.
#  The Track_1 function is a state machine that uses sensor data (line sensor, IMU, encoders)
#  and a PID controller to follow a line, execute turns, and handle bumps.
#

from pid import PID
from imu import BNO055
from pyb import ExtInt, Pin
from time import ticks_us

## @brief Main task function for autonomous navigation.
#  @param shares A dictionary with shared objects: 'motorL', 'motorR', 'sensor_array', 'imu', 'encoderL', 'encoderR'.
def Track_1(shares):
    motorL = shares['motorL']
    motorR = shares['motorR']
    linesensor = shares['sensor_array']
    imu = shares['imu']
    encoderL = shares['encoderL']
    encoderR = shares['encoderR']

    # Define state constants.
    s = 0 
    s0 = 0  # Initialization
    s1 = 1  # Follow line
    s2 = 2  # Rotate 180° from origin
    s3 = 3  # Go straight
    s4 = 4  # Turn 90° right
    s5 = 5  # Go straight
    s6 = 6  # Follow line until wall detected
    s7 = 7  # Back up
    s8 = 8  # Turn right 90°
    s9 = 9  # Go straight
    s10 = 10  # Turn left 90°
    s11 = 11  # Look for and follow line
    s13 = 12  # Go straight until end or bump
    error1 = 13  # Bump detected
    
    default_effort = 30
    bounds = 50

    motorL.set_effort(default_effort)
    motorR.set_effort(default_effort)
    motorL.enable()
    motorR.enable()
    
    while True:
        encoderL.update()
        
        ## State s0: Initialization.
        if s == s0:
            pos = None
            desired_angle = None
            s = s1  # Transition to follow line.
            dt = 0.01  # 10 ms period (100Hz).
            desired_value = 3.4
            pid_1 = PID(kp=15, ki=0.001, kd=0.001, setpoint=desired_value, dt=dt, output_limits=(-bounds, bounds))
        
        ## State s1: Follow line.
        if s == s1:
            centroid = linesensor.compute_centroid()
            correction = pid_1.update(centroid)
            if encoderL.get_position() >= 4050: 
                s = s2
            elif encoderL.get_position() >= 1045 and not encoderL.get_position() > 1185:
                print("ignore diamond")
                pid_1 = PID(kp=15, ki=0.001, kd=0.001, setpoint=desired_value, dt=dt, output_limits=(-bounds, bounds))
                new_effort_left = default_effort 
                new_effort_right = default_effort
            elif correction > 0.5:
                new_effort_right = default_effort - int(correction)
                new_effort_left = default_effort + int(correction)
            elif correction < -0.5:
                new_effort_right = default_effort - int(correction)
                new_effort_left = default_effort + int(correction)
            else:
                new_effort_left = default_effort 
                new_effort_right = default_effort
            motorL.set_effort(new_effort_left)
            motorR.set_effort(new_effort_right)
            yield
        
        ## State s2: Rotate to 180° from origin.
        if s == s2:
            if desired_angle is None:
                desired_angle = imu.getEuler()[0]
            current_angle = imu.getEuler()[0]
            target_angle = (imu.center + 2880) % 5760  # 180° offset.
            error = (current_angle - target_angle + 2880) % 5800 - 2880
            if abs(error) > 50:
                motorL.set_effort(-15)
                motorR.set_effort(15)
            else:
                motorL.set_effort(0)
                motorR.set_effort(0)
                t1 = ticks_us()
                s = s3
                desired_angle = None
            yield
        
        ## State s3: Go straight for a set amount.
        if s == s3:
            if pos is None:
                pos = encoderL.get_position()
                goal = pos + 690
            if encoderL.get_position() > goal:
                pos = None
                s = s4
                motorR.set_effort(0)
                motorL.set_effort(0)
            else:
                error = (target_angle - imu.getEuler()[0] + 2880) % 5760 - 2880
                if abs(error) > 20:
                    correction = 0.1 * error
                    motorL.set_effort(20 + correction)
                    motorR.set_effort(20 - correction)
                else:
                    motorL.set_effort(20)
                    motorR.set_effort(20)
            yield
        
        ## State s4: Turn 90° right.
        if s == s4:
            print("state 4")
            current_angle = imu.getEuler()[0]
            target_angle1 = (current_angle + 1440) % 5760  # 90° turn.
            while abs(imu.getEuler()[0] - target_angle1) > 50:
                motorL.set_effort(20)
                motorR.set_effort(-20)
                yield
            motorL.set_effort(20)
            motorR.set_effort(20)
            s = s5
            yield
        
        ## State s5: Go straight.
        if s == s5:
            if pos is None:
                pos = encoderL.get_position()
                goal = pos + 200
                current_angle5 = imu.getEuler()[0]
            error = (current_angle5 - imu.getEuler()[0]) % 5760
            if imu.getAccel()[0] >= 250:
                print("Bump Detected.")
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = error1
            if encoderL.get_position() > goal:
                pid_1 = PID(kp=15, ki=0.001, kd=0.001, setpoint=desired_value, dt=dt, output_limits=(-bounds, bounds))
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = s6
            yield
        
        ## State s6: Follow line until wall detected.
        if s == s6:
            centroid = linesensor.compute_centroid()
            correction = pid_1.update(centroid)
            if imu.getAccel()[0] >= 250:
                print("Bump Detected.")
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = s7
            elif correction > 0.5:
                new_effort_right = default_effort - int(correction)
                new_effort_left = default_effort + int(correction)
            elif correction < -0.5:
                new_effort_right = default_effort - int(correction)
                new_effort_left = default_effort + int(correction)
            else:
                new_effort_left = default_effort 
                new_effort_right = default_effort
            motorL.set_effort(new_effort_left)
            motorR.set_effort(new_effort_right)
            yield
        
        ## State s7: Wall detected and back up.
        if s == s7:
            if pos is None:
                pos = encoderL.get_position()
                goal = pos - 70
            motorL.set_effort(-20)
            motorR.set_effort(-20)
            if encoderL.get_position() < goal:
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = s8
            yield
        
        ## State s8: Turn right 90°.
        if s == s8:
            target_angle = imu.center
            while abs(imu.getEuler()[0] - target_angle) > 50:
                motorL.set_effort(20)
                motorR.set_effort(-20)
                yield
            motorL.set_effort(0)
            motorR.set_effort(0)
            s = s9
            yield
        
        ## State s9: Go straight for a set amount.
        if s == s9:
            if pos is None:
                pos = encoderL.get_position()
                goal = pos + 600
            motorL.set_effort(20)
            motorR.set_effort(22)
            if encoderL.get_position() > goal:
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = s10
            yield
        
        ## State s10: Rotate left 90°.
        if s == s10:
            current_angle = imu.getEuler()[0]
            target_angle = (current_angle - 1500) % 5760
            while abs(imu.getEuler()[0] - target_angle) > 50:
                motorL.set_effort(-20)
                motorR.set_effort(20)
                yield
            motorL.set_effort(0)
            motorR.set_effort(0)
            s = s11
            yield
        
        ## State s11: Move forward for a set amount.
        if s == s11:
            if pos is None:
                pos = encoderL.get_position()
                goal = pos + 110
            motorL.set_effort(default_effort)
            motorR.set_effort(default_effort + 1)
            if encoderL.get_position() > goal:
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                pid_1.setpoint = 3
                s = s13
            yield
        
        ## State s13: Follow line until end or bump.
        if s == s13:
            centroid = linesensor.compute_centroid()
            correction1 = pid_1.update(centroid)
            if imu.getAccel()[0] >= 250:
                print("WE DONE BABBYYY")
                motorR.set_effort(0)
                motorL.set_effort(0)
            elif correction1 > 0.5:
                new_effort_right = default_effort - int(correction1)
                new_effort_left = default_effort + int(correction1)
            elif correction1 < -0.5:
                new_effort_right = default_effort - int(correction1)
                new_effort_left = default_effort + int(correction1)
            else:
                new_effort_left = default_effort 
                new_effort_right = default_effort
            motorL.set_effort(new_effort_left)
            motorR.set_effort(new_effort_right)
            yield
        
        ## State error1: Bump detected.
        if s == error1:
            print("bump detected")
            yield
