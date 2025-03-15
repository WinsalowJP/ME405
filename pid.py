class PID:
    def __init__(self, kp, ki, kd, setpoint, dt, output_limits=(None, None)):
        self.kp = kp              # Proportional gain
        self.ki = ki              # Integral gain
        self.kd = kd              # Derivative gain
        self.setpoint = setpoint  # Desired target value
        self.dt = dt              # Time interval between updates (seconds)
        self.output_limits = output_limits  # Tuple (min, max) for output clamping

        self.integral = 0
        self.previous_error = 0

    def update(self, measured_value):
        # Calculate error
        error = self.setpoint - measured_value
        
        # Integrate error over time
        self.integral += error * self.dt
        
        # Derivative term based on error change
        derivative = (error - self.previous_error) / self.dt
        
        # PID output
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        
        # Save error for the next cycle
        self.previous_error = error
        
        # Clamp output if limits are set
        lower, upper = self.output_limits
        if lower is not None:
            output = max(lower, output)
        if upper is not None:
            output = min(upper, output)
            
        return output

    def setpoint(self, setpoint):
        self.setpoint = setpoint
