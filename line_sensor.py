"""
@file linesensor.py
@brief Implements line sensor functionality for reading, calibrating, and processing sensor data.

This module defines two classes:
 - LineSensor: Manages a single line sensor connected to an ADC pin.
 - LineSensorArray: Manages an array of line sensors, providing methods for calibration,
   reading raw and normalized values, computing the centroid of a detected line, and
   saving/loading calibration data.
"""

from pyb import ADC, Pin, delay

class LineSensor:
    """
    @brief Represents a single line sensor connected to an ADC pin.

    The LineSensor class handles reading raw values from the sensor, calibrating the sensor values,
    and normalizing readings based on calibration limits (white and black values).
    """
    
    def __init__(self, pin, white=4095, black=0):
        """
        @brief Initializes a LineSensor object.

        Configures the ADC for the specified pin and sets default calibration limits.
        
        @param pin The pin identifier where the sensor is connected.
        @param white The default maximum value (white) for calibration.
        @param black The default minimum value (black) for calibration.
        """
        # Initialize the ADC for the given pin.
        self.adc = ADC(Pin(pin))
        # Set calibration limits (default if no file is loaded).
        self.white = white  
        self.black = black  
    
    def read_raw(self):
        """
        @brief Reads the raw analog value from the line sensor.
        
        @return The raw ADC reading from the sensor.
        """
        return self.adc.read()
    
    def calibrate_value(self, sample):
        """
        @brief Updates calibration limits based on a new sample.

        Adjusts the 'white' and 'black' calibration values if the new sample is lower or higher
        than the current calibration limits.
        
        @param sample The raw sensor value to be used for calibration.
        """
        if sample < self.white:
            self.white = sample
        if sample > self.black:
            self.black = sample
    
    def normalize(self, raw):
        """
        @brief Normalizes a raw sensor value to a range between 0 and 1 based on calibration limits.

        If the calibration range is non-zero, the function scales the raw value accordingly.
        Otherwise, it returns 0.
        
        @param raw The raw sensor reading.
        @return The normalized sensor value clamped between 0 and 1.
        """
        if (self.black - self.white) != 0:
            norm = (raw - self.white) / (self.black - self.white)
            return max(0, min(1, norm))
        else:
            return 0

class LineSensorArray:
    """
    @brief Manages an array of line sensors.

    This class provides methods for calibrating all sensors, reading raw and normalized values,
    computing the centroid of a detected line, and saving/loading calibration data to/from a file.
    """
    
    def __init__(self, pin_list):
        """
        @brief Initializes a LineSensorArray with a list of pins.

        Each pin in the list is used to instantiate a LineSensor object.
        Calibration data is loaded from a file if available.
        
        @param pin_list A list of pin identifiers for each sensor in the array.
        """
        self.sensors = [LineSensor(pin) for pin in pin_list]
        self.calibration_file = "line_calibration.txt"
        self.load_calibration()  # Load calibration at startup
    
    def calibrate(self, samples=50, delay_ms=20):
        """
        @brief Calibrates all sensors in the array over a series of samples.

        For each sample, each sensor's calibration values are updated, then the process waits for
        a specified delay before taking the next sample. Calibration data is saved after completion.
        
        @param samples The number of calibration samples to take (default is 50).
        @param delay_ms The delay in milliseconds between each sample (default is 20 ms).
        """
        for _ in range(samples):
            for sensor in self.sensors:
                sample = sensor.read_raw()
                sensor.calibrate_value(sample)
            delay(delay_ms)
        self.save_calibration()  # Save after calibration
    
    def read_raw(self):
        """
        @brief Reads raw values from all sensors in the array.
        
        @return A list of raw ADC readings, one per sensor.
        """
        return [sensor.read_raw() for sensor in self.sensors]
    
    def get_normalized_values(self):
        """
        @brief Retrieves normalized sensor values for all sensors.
        
        @return A list of normalized values (between 0 and 1) for each sensor.
        """
        raw_values = self.read_raw()
        return [sensor.normalize(raw) for sensor, raw in zip(self.sensors, raw_values)]
    
    def compute_centroid(self):
        """
        @brief Computes the centroid of the line detected by the sensor array.

        The centroid is computed based on normalized sensor values and weighted by sensor positions.
        If no line is detected, the centroid defaults to the center of the sensor array.
        
        @return The computed centroid value.
        """
        norm_values = self.get_normalized_values()
        total = sum(norm_values)

        if total == 0:
            return (len(self.sensors) - 1) / 2  # Default to center if no line is detected

        num_sensors = len(self.sensors)
        center_index = (num_sensors - 1) / 2
        weights = [1 / (1 + abs(i - center_index)) for i in range(num_sensors)]

        weighted_values = [val * weights[i] for i, val in enumerate(norm_values)]
        weighted_total = sum(weighted_values)

        if weighted_total == 0:
            return center_index  # Prevent division by zero

        weighted_sum = sum(i * weighted_values[i] for i in range(num_sensors))
        return weighted_sum / weighted_total
    
    def line_detected(self, threshold, min_active):
        """
        @brief Determines if a line is detected based on sensor thresholds.

        Counts the number of sensors with normalized values above a specified threshold and compares
        it to the minimum number required to consider that a line is detected.
        
        @param threshold The normalized value threshold to consider a sensor as active.
        @param min_active The minimum number of active sensors required to detect a line.
        @return True if the number of active sensors meets or exceeds min_active; otherwise, False.
        """
        norm_values = self.get_normalized_values()
        active = sum(1 for val in norm_values if val > threshold)
        return active >= min_active
    
    def save_calibration(self):
        """
        @brief Saves the calibration values for all sensors to a file.

        Writes the 'white' and 'black' calibration values for each sensor to the specified file.
        """
        try:
            with open(self.calibration_file, "w") as f:
                for sensor in self.sensors:
                    f.write(f"{sensor.white},{sensor.black}\n")
            print("Calibration saved successfully.")
        except Exception as e:
            print(f"Error saving calibration: {e}")

    def load_calibration(self):
        """
        @brief Loads calibration values from a file for all sensors.

        Reads the calibration file and updates each sensor's calibration values. If the number of lines in
        the file does not match the number of sensors, a warning is printed.
        """
        try:
            with open(self.calibration_file, "r") as f:
                lines = f.readlines()
                if len(lines) == len(self.sensors):  # Ensure matching number of sensors
                    for i, line in enumerate(lines):
                        white, black = map(int, line.strip().split(","))
                        self.sensors[i].white = white
                        self.sensors[i].black = black
                    print("Calibration loaded successfully.")
                else:
                    print("Calibration file mismatch. Recalibrate sensors.")
        except Exception as e:
            print(f"Error loading calibration: {e}")
