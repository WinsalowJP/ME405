## @file pid.py
#  This file implements a PID controller for process control.
#  It calculates the controller output based on the proportional, integral, and derivative terms.
#

class PID:
    ## @brief Initializes a new PID controller instance.
    #  
    #  @param kp Proportional gain.
    #  @param ki Integral gain.
    #  @param kd Derivative gain.
    #  @param setpoint The desired target value.
    #  @param dt Time interval between updates (seconds).
    #  @param output_limits A tuple (min, max) for output clamping.
    def __init__(self, kp, ki, kd, setpoint, dt, output_limits=(None, None)):
        self.kp = kp              # Proportional gain
        self.ki = ki              # Integral gain
        self.kd = kd              # Derivative gain
        self.setpoint = setpoint  # Desired target value
        self.dt = dt              # Time interval (seconds)
        self.output_limits = output_limits  # Output clamping limits

        self.integral = 0
        self.previous_error = 0

    ## @brief Updates the PID controller and computes the output.
    #  @param measured_value The current measured process value.
    #  @return The computed PID output (clamped if limits are set).
    def update(self, measured_value):
        error = self.setpoint - measured_value  # Calculate error
        self.integral += error * self.dt          # Integrate error
        derivative = (error - self.previous_error) / self.dt  # Derivative term

        output = self.kp * error + self.ki * self.integral + self.kd * derivative  # PID output

        self.previous_error = error  # Update error for next cycle

        # Clamp output if limits are defined.
        lower, upper = self.output_limits
        if lower is not None:
            output = max(lower, output)
        if upper is not None:
            output = min(upper, output)
            
        return output

    ## @brief Updates the desired setpoint for the PID controller.
    #  @param setpoint The new target value.
    def setpoint(self, setpoint):
        self.setpoint = setpoint
