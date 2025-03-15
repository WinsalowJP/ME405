from pid import PID
from imu import BNO055
from pyb import ExtInt, Pin
from time import ticks_us

def Track_1(shares):
    motorL = shares['motorL']
    motorR = shares['motorR']
    linesensor = shares['sensor_array']
    imu = shares['imu']
    encoderL = shares['encoderL']
    encoderR = shares['encoderR']

    s = 0 
    s0 = 0 #init
    s1 = 1 # follow line
    s2 = 2 # rotate to 180 from origin
    s3 = 3 #go straight
    s4 = 4 #turn 90 right
    s5= 5 #go straight 
    s6 = 6 #follow line until wall detected
    s7 = 7 #back up
    s8 = 8 #turn right 90 degrees
    s9 = 9 #go straight
    s10 = 10 #turn left 90 degrees
    s11 = 11 # look for and follow line
    s13 = 12 #straight till the end or bump
    error1 = 13 #bump detected
    default_effort = 30
    bounds = 50
    
    motorL.set_effort(default_effort)
    motorR.set_effort(default_effort)
    motorL.enable()
    motorR.enable()
    while True:
        encoderL.update()       
        if s == s0: #init
            pos = None
            desired_angle = None
            s = 1
            dt = 0.01  # 10 ms period (100Hz)
            desired_value = 3.4
            
            pid_1 = PID(kp=15, ki=.001, kd=0.001, setpoint=desired_value, dt=dt, output_limits=(-bounds,  bounds))
# -------------------follow line for set amount -------------------
        if s == s1:
            centroid = (linesensor.compute_centroid())
            correction = pid_1.update(centroid)

            if encoderL.get_position() >= 4050: 
                s = s2
            elif encoderL.get_position() >= 1045 and not encoderL.get_position() > 1185:
                print("ignore diamond")
                pid_1 = PID(kp=15, ki=.001, kd=0.001, setpoint=desired_value, dt=dt, output_limits=(-bounds,  bounds))
                new_effort_left = default_effort 
                new_effort_right = default_effort
            elif correction > .5: #basic line following
                new_effort_right = default_effort - (int(correction))
                new_effort_left = default_effort  + ((int(correction)))
            elif correction < -.5:
                new_effort_right = default_effort - (int(correction))
                new_effort_left = default_effort + (int(correction))
            else:
                new_effort_left = default_effort 
                new_effort_right = default_effort
            motorL.set_effort(new_effort_left)
            motorR.set_effort(new_effort_right)
            yield

#--------------------------------align with 180 degrees from origin ------------------------
        if s == s2:
            if desired_angle==None:
                desired_angle = imu.getEuler()[0] 
            current_angle = imu.getEuler()[0]
            target_angle = (imu.center + 2880)  % 5760 #180 degree
            error = (current_angle - target_angle + 2880) % 5800 - 2880
            if abs(error) > 50:  # Allow small margin
                motorL.set_effort(-15)
                motorR.set_effort(15)  # Rotate right
            else:
                motorL.set_effort(0)
                motorR.set_effort(0)
                t1 = ticks_us()
                s = s3
                desired_angle=None
            
            yield
#------------------- go straight for set amount -----------------------------
        if s == s3:
            if pos == None:
                pos = encoderL.get_position()
                goal = pos + 690  

            if (encoderL.get_position()>goal):
                pos = None
                s = s4
                motorR.set_effort(0)
                motorL.set_effort(0)  
            else:
                error = (target_angle - imu.getEuler()[0] + 2880) % 5760 - 2880
                if abs(error) > 20:
                    correction = 0.1 * error
                    # Adjust the motor efforts proportionally
                    motorL.set_effort(20 + correction)
                    motorR.set_effort(20 - correction)
                else:
                    # If within margin, maintain straight motion at base_speed
                    motorL.set_effort(20)
                    motorR.set_effort(20)
            yield
#------------------turn 90 degrees right ----------------------------            

        if s == s4:  # Turn 90 degrees to the right using Euler angles
                print("state 4")
                current_angle = imu.getEuler()[0]
                target_angle1 = (current_angle + 1440) % 5760  # 90-degree turn
                while abs(imu.getEuler()[0] - target_angle1) > 50:  # Allow small margin
                    motorL.set_effort(20)
                    motorR.set_effort(-20)  # Rotate right
                    yield
                motorL.set_effort(20)
                motorR.set_effort(20)
                s = s5  # Move to state 6 after turning
                yield

#----------- go straight ---------------
        if s == s5:
            if pos == None:
                pos = encoderL.get_position()
                goal = pos + 200
                current_angle5 = imu.getEuler()[0]
            error = (current_angle5 - imu.getEuler()[0]) % 5760
            if(imu.getAccel()[0]>=250): #if forward
                print("Bump Detected.")
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = error1
            if (encoderL.get_position() > goal):
                pid_1 = PID(kp=15, ki=.001, kd=0.001, setpoint=desired_value, dt=dt, output_limits=(-bounds,  bounds))
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = s6
            yield
# ------------follow line untill wall-----------------------
        if s == s6:
            centroid = (linesensor.compute_centroid())
            correction = pid_1.update(centroid)

            if(imu.getAccel()[0]>=250): #if forward
                print("Bump Detected.")
                motorR.set_effort(0)
                motorL.set_effort(0)
                s=s7
            elif correction > .5: #basic line following
                new_effort_right = default_effort - (int(correction))
                new_effort_left = default_effort  + ((int(correction)))
            elif correction < -.5:
                new_effort_right = default_effort - (int(correction))
                new_effort_left = default_effort + (int(correction))
            else:
                new_effort_left = default_effort 
                new_effort_right = default_effort
            motorL.set_effort(new_effort_left)
            motorR.set_effort(new_effort_right)
            yield

# ------------wall detected and back up-----------------------
        if s==s7:
            if pos == None:
                pos = encoderL.get_position()
                goal = pos - 70  
            motorL.set_effort(-20)
            motorR.set_effort(-20)
            if (encoderL.get_position()<goal):
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                s=s8
            yield

# ------------turn right 90 degrees-----------------------
        if s==s8:
            target_angle = (imu.center) # 90-degree turn

            while abs(imu.getEuler()[0] - target_angle) > 50:  # Allow small margin
                motorL.set_effort(20)
                motorR.set_effort(-20)  # Rotate right
                yield
            motorL.set_effort(0)
            motorR.set_effort(0)
        
            s = s9  # Move to state 9 after turning
            yield

# --------- go straight for set amount -------------------
        if s==s9:
            if pos == None:
                pos = encoderL.get_position()
                goal = pos + 600  

            motorL.set_effort(20)
            motorR.set_effort(22)

            if (encoderL.get_position()>goal):
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                s=s10
            yield
# ------------- rotate left 90 degrees -------------------
        if s==s10:
            current_angle = imu.getEuler()[0]
            target_angle = (current_angle - 1500) % 5760  # 90-degree turn
            while abs(imu.getEuler()[0] - target_angle) > 50:  # Allow small margin
                motorL.set_effort(-20)# Rotate left
                motorR.set_effort(20)  
                yield
            motorL.set_effort(0)
            motorR.set_effort(0)
            s = s11  
            yield

# ------------move fowarda set amount-------------------
        if s==s11:
            if pos == None:
                pos = encoderL.get_position()
                goal = pos + 110  

            motorL.set_effort(default_effort)
            motorR.set_effort(default_effort+1)

            if (encoderL.get_position()>goal):
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                pid_1.setpoint = 3
                s=s13
            yield
# ------------follow line -------------------
        if s == s13:
            centroid = (linesensor.compute_centroid())
            correction1 = pid_1.update(centroid)

            if(imu.getAccel()[0]>=250): #if forward
                print("WE DONE BABBYYY")
                motorR.set_effort(0)
                motorL.set_effort(0)
                
            elif correction > .5: #basic line following
                new_effort_right = default_effort - (int(correction1))
                new_effort_left = default_effort  + ((int(correction1)))
            elif correction < -.5:
                new_effort_right = default_effort - (int(correction1))
                new_effort_left = default_effort + (int(correction1))
            else:
                new_effort_left = default_effort 
                new_effort_right = default_effort
            motorL.set_effort(new_effort_left)
            motorR.set_effort(new_effort_right)
            yield
#------------------bump detected -------------------
        if s == error1:
            print("bump detected")
            yield
