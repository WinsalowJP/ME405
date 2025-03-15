"""
@brief Main task function for autonomous tracking and navigation.

This function implements a state machine to control motor actions based on sensor feedback.
It uses data from a line sensor array, an IMU, and encoders to follow a line, make turns,
and respond to bumps. The function transitions through multiple states (s0 to s13 and error1)
to perform tasks such as initializing, following a line, rotating to a specific angle, moving straight,
and handling bumps.

@param shares A dictionary containing shared objects used in the task:
              - 'motorL': Left motor object.
              - 'motorR': Right motor object.
              - 'sensor_array': Line sensor array.
              - 'imu': IMU sensor object.
              - 'encoderL': Left encoder object.
              - 'encoderR': Right encoder object.
"""
def Track_1(shares):
    # Retrieve shared objects for motor, sensor, IMU, and encoders.
    motorL = shares['motorL']
    motorR = shares['motorR']
    linesensor = shares['sensor_array']
    imu = shares['imu']
    encoderL = shares['encoderL']
    encoderR = shares['encoderR']

    # Define state constants for clarity.
    s = 0      # Current state: initialization
    s0 = 0     # Initialization state
    s1 = 1     # Follow line
    s2 = 2     # Rotate to 180 degrees from origin
    s3 = 3     # Go straight
    s4 = 4     # Turn 90 degrees right
    s5 = 5     # Go straight
    s6 = 6     # Follow line until wall detected
    s7 = 7     # Back up
    s8 = 8     # Turn right 90 degrees
    s9 = 9     # Go straight
    s10 = 10   # Turn left 90 degrees
    s11 = 11   # Look for and follow line
    s13 = 12   # Go straight till the end or bump
    error1 = 13  # Bump detected state
    
    # Default motor effort and control bounds.
    default_effort = 30
    bounds = 50
    
    # Set initial motor efforts and enable motors.
    motorL.set_effort(default_effort)
    motorR.set_effort(default_effort)
    motorL.enable()
    motorR.enable()
    
    # Main loop of the state machine.
    while True:
        encoderL.update()  # Update encoder readings

        # ---------------------- State s0: Initialization ----------------------
        if s == s0: 
            # Variables initialization.
            pos = None
            desired_angle = None
            s = 1  # Transition to state s1: follow line
            dt = 0.01  # Set update period to 10 ms (100Hz)
            desired_value = 3.4  # Desired centroid value for line following
            
            # Initialize a PID controller for line following.
            pid_1 = PID(kp=15, ki=.001, kd=0.001, setpoint=desired_value, dt=dt, output_limits=(-bounds, bounds))
        
        # ---------------------- State s1: Follow line ----------------------
        if s == s1:
            # Compute line centroid and update PID controller.
            centroid = linesensor.compute_centroid()
            correction = pid_1.update(centroid)
            
            # Transition conditions based on encoder position.
            if encoderL.get_position() >= 4050: 
                s = s2
            elif encoderL.get_position() >= 1045 and not encoderL.get_position() > 1185:
                print("ignore diamond")
                # Reset PID controller and maintain default efforts.
                pid_1 = PID(kp=15, ki=.001, kd=0.001, setpoint=desired_value, dt=dt, output_limits=(-bounds, bounds))
                new_effort_left = default_effort 
                new_effort_right = default_effort
            # Adjust motor efforts based on PID correction.
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

        # ---------------------- State s2: Rotate to 180 degrees from origin ----------------------
        if s == s2:
            if desired_angle == None:
                # Capture initial angle as reference.
                desired_angle = imu.getEuler()[0]
            current_angle = imu.getEuler()[0]
            # Calculate target angle: 180 degrees offset from the initial center.
            target_angle = (imu.center + 2880) % 5760  # 2880 ticks corresponds to 180 degrees
            error = (current_angle - target_angle + 2880) % 5800 - 2880
            if abs(error) > 50:  # Allow small margin for rotation.
                motorL.set_effort(-15)
                motorR.set_effort(15)  # Rotate right.
            else:
                motorL.set_effort(0)
                motorR.set_effort(0)
                t1 = ticks_us()  # Time stamp (unused further in this snippet)
                s = s3  # Transition to state s3: go straight
                desired_angle = None
            yield

        # ---------------------- State s3: Go straight for a set amount ----------------------
        if s == s3:
            if pos == None:
                pos = encoderL.get_position()
                goal = pos + 690  # Set a goal based on encoder ticks.
            if encoderL.get_position() > goal:
                pos = None
                s = s4  # Transition to state s4: turn 90 degrees right.
                motorR.set_effort(0)
                motorL.set_effort(0)
            else:
                # Correct orientation based on IMU Euler angles.
                error = (target_angle - imu.getEuler()[0] + 2880) % 5760 - 2880
                if abs(error) > 20:
                    correction = 0.1 * error
                    motorL.set_effort(20 + correction)
                    motorR.set_effort(20 - correction)
                else:
                    motorL.set_effort(20)
                    motorR.set_effort(20)
            yield

        # ---------------------- State s4: Turn 90 degrees right ----------------------
        if s == s4:
            print("state 4")
            current_angle = imu.getEuler()[0]
            target_angle1 = (current_angle + 1440) % 5760  # 1440 ticks corresponds to 90 degrees.
            while abs(imu.getEuler()[0] - target_angle1) > 50:  # Allow margin.
                motorL.set_effort(20)
                motorR.set_effort(-20)  # Rotate right.
                yield
            motorL.set_effort(20)
            motorR.set_effort(20)
            s = s5  # Transition to state s5.
            yield

        # ---------------------- State s5: Go straight ----------------------
        if s == s5:
            if pos == None:
                pos = encoderL.get_position()
                goal = pos + 200  # Set goal distance.
                current_angle5 = imu.getEuler()[0]
            error = (current_angle5 - imu.getEuler()[0]) % 5760
            # Check for a bump using accelerometer data.
            if imu.getAccel()[0] >= 250:
                print("Bump Detected.")
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = error1  # Transition to bump detected state.
            if encoderL.get_position() > goal:
                pid_1 = PID(kp=15, ki=.001, kd=0.001, setpoint=desired_value, dt=dt, output_limits=(-bounds, bounds))
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = s6  # Transition to state s6: follow line until wall.
            yield

        # ---------------------- State s6: Follow line until wall detected ----------------------
        if s == s6:
            centroid = linesensor.compute_centroid()
            correction = pid_1.update(centroid)
            if imu.getAccel()[0] >= 250:  # Detect bump.
                print("Bump Detected.")
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = s7  # Transition to backup state.
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

        # ---------------------- State s7: Wall detected and back up ----------------------
        if s == s7:
            if pos == None:
                pos = encoderL.get_position()
                goal = pos - 70  # Set backup distance.
            motorL.set_effort(-20)
            motorR.set_effort(-20)
            if encoderL.get_position() < goal:
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = s8  # Transition to state s8: turn right 90 degrees.
            yield

        # ---------------------- State s8: Turn right 90 degrees ----------------------
        if s == s8:
            target_angle = imu.center  # Target angle for a 90-degree turn.
            while abs(imu.getEuler()[0] - target_angle) > 50:  # Allow margin.
                motorL.set_effort(20)
                motorR.set_effort(-20)  # Rotate right.
                yield
            motorL.set_effort(0)
            motorR.set_effort(0)
            s = s9  # Transition to state s9: go straight.
            yield

        # ---------------------- State s9: Go straight for a set amount ----------------------
        if s == s9:
            if pos == None:
                pos = encoderL.get_position()
                goal = pos + 600  # Set distance goal.
            motorL.set_effort(20)
            motorR.set_effort(22)
            if encoderL.get_position() > goal:
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                s = s10  # Transition to state s10: turn left 90 degrees.
            yield

        # ---------------------- State s10: Rotate left 90 degrees ----------------------
        if s == s10:
            current_angle = imu.getEuler()[0]
            target_angle = (current_angle - 1500) % 5760  # 90-degree turn.
            while abs(imu.getEuler()[0] - target_angle) > 50:  # Allow margin.
                motorL.set_effort(-20)  # Rotate left.
                motorR.set_effort(20)
                yield
            motorL.set_effort(0)
            motorR.set_effort(0)
            s = s11  # Transition to state s11.
            yield

        # ---------------------- State s11: Move forward for a set amount ----------------------
        if s == s11:
            if pos == None:
                pos = encoderL.get_position()
                goal = pos + 110  # Set goal distance.
            motorL.set_effort(default_effort)
            motorR.set_effort(default_effort + 1)
            if encoderL.get_position() > goal:
                pos = None
                motorR.set_effort(0)
                motorL.set_effort(0)
                # Update PID setpoint before transitioning.
                pid_1.setpoint = 3
                s = s13  # Transition to state s13: follow line.
            yield

        # ---------------------- State s13: Follow line until end or bump ----------------------
        if s == s13:
            centroid = linesensor.compute_centroid()
            correction1 = pid_1.update(centroid)
            if imu.getAccel()[0] >= 250:  # Detect bump.
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

        # ---------------------- State error1: Bump detected ----------------------
        if s == error1:
            print("bump detected")
            yield
