"""
@file pid.py
@brief Implements a PID controller for process control.

This module defines a PID class that provides proportional-integral-derivative (PID)
control for a given setpoint. The controller calculates an output based on the error,
integral, and derivative terms.
"""

class PID:
    """
    @brief A PID controller class.

    This class implements a PID controller with methods to update the controller output
    based on the measured process value and to adjust the setpoint.
    """

    def __init__(self, kp, ki, kd, setpoint, dt, output_limits=(None, None)):
        """
        @brief Initializes a new PID controller instance.

        Sets up the PID gains, setpoint, time interval between updates, and optional
        output limits.

        @param kp Proportional gain.
        @param ki Integral gain.
        @param kd Derivative gain.
        @param setpoint The desired target value.
        @param dt The time interval between updates in seconds.
        @param output_limits A tuple (min, max) used to clamp the PID output. Default is (None, None).
        """
        self.kp = kp              # Proportional gain
        self.ki = ki              # Integral gain
        self.kd = kd              # Derivative gain
        self.setpoint = setpoint  # Desired target value
        self.dt = dt              # Time interval between updates (seconds)
        self.output_limits = output_limits  # Tuple (min, max) for output clamping

        self.integral = 0
        self.previous_error = 0

    def update(self, measured_value):
        """
        @brief Updates the PID controller with the measured value and computes the new output.

        This method calculates the error between the setpoint and the measured value,
        integrates the error, computes the derivative, and then calculates the PID output.
        It also clamps the output within the specified limits if they are set.

        @param measured_value The current measured value of the process variable.
        @return The computed PID output after clamping.
        """
        # Calculate error between setpoint and measured value
        error = self.setpoint - measured_value
        
        # Integrate error over time
        self.integral += error * self.dt
        
        # Derivative term based on error change
        derivative = (error - self.previous_error) / self.dt
        
        # PID output calculation
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
        """
        @brief Updates the desired setpoint for the PID controller.

        @param setpoint The new desired target value.
        """
        self.setpoint = setpoint
