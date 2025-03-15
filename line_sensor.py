## @file line_sensor.py
#  This file implements classes to interact with line sensors.
#  It includes functionality for reading raw values, calibration, normalization,
#  and computing the centroid of a detected line.
#
 

from pyb import ADC, Pin, delay

## @brief Represents a single line sensor connected to an ADC pin.
class LineSensor:
    ## @brief Initializes a LineSensor object.
    #  @param pin The ADC pin identifier.
    #  @param white Default maximum calibration value (white).
    #  @param black Default minimum calibration value (black).
    def __init__(self, pin, white=4095, black=0):
        self.adc = ADC(Pin(pin))  # Initialize ADC
        self.white = white         # White calibration limit
        self.black = black         # Black calibration limit
    
    ## @brief Reads the raw sensor value.
    #  @return The raw ADC reading.
    def read_raw(self):
        return self.adc.read()
    
    ## @brief Updates calibration values based on a new sample.
    #  @param sample The raw sensor value.
    def calibrate_value(self, sample):
        if sample < self.white:
            self.white = sample
        if sample > self.black:
            self.black = sample
    
    ## @brief Normalizes a raw value between 0 and 1.
    #  @param raw The raw sensor value.
    #  @return The normalized value.
    def normalize(self, raw):
        if (self.black - self.white) != 0:
            norm = (raw - self.white) / (self.black - self.white)
            return max(0, min(1, norm))
        else:
            return 0

## @brief Manages an array of line sensors.
class LineSensorArray:
    ## @brief Initializes the LineSensorArray.
    #  @param pin_list A list of ADC pin identifiers for each sensor.
    def __init__(self, pin_list):
        self.sensors = [LineSensor(pin) for pin in pin_list]
        self.calibration_file = "line_calibration.txt"
        self.load_calibration()  # Load calibration on startup
    
    ## @brief Calibrates all sensors over a series of samples.
    #  @param samples Number of samples to take.
    #  @param delay_ms Delay between samples in milliseconds.
    def calibrate(self, samples=50, delay_ms=20):
        for _ in range(samples):
            for sensor in self.sensors:
                sample = sensor.read_raw()
                sensor.calibrate_value(sample)
            delay(delay_ms)
        self.save_calibration()  # Save calibration data after calibration
    
    ## @brief Reads raw values from all sensors.
    #  @return A list of raw sensor readings.
    def read_raw(self):
        return [sensor.read_raw() for sensor in self.sensors]
    
    ## @brief Gets normalized sensor values.
    #  @return A list of normalized sensor values.
    def get_normalized_values(self):
        raw_values = self.read_raw()
        return [sensor.normalize(raw) for sensor, raw in zip(self.sensors, raw_values)]
    
    ## @brief Computes the centroid of the detected line.
    #  @return The computed centroid value.
    def compute_centroid(self):
        norm_values = self.get_normalized_values()
        total = sum(norm_values)
        if total == 0:
            return (len(self.sensors) - 1) / 2  # Default center if no line detected
        num_sensors = len(self.sensors)
        center_index = (num_sensors - 1) / 2
        weights = [1 / (1 + abs(i - center_index)) for i in range(num_sensors)]
        weighted_values = [val * weights[i] for i, val in enumerate(norm_values)]
        weighted_total = sum(weighted_values)
        if weighted_total == 0:
            return center_index
        weighted_sum = sum(i * weighted_values[i] for i in range(num_sensors))
        return weighted_sum / weighted_total
    
    ## @brief Determines if a line is detected.
    #  @param threshold Normalized threshold value.
    #  @param min_active Minimum number of sensors that must be active.
    #  @return True if a line is detected, False otherwise.
    def line_detected(self, threshold, min_active):
        norm_values = self.get_normalized_values()
        active = sum(1 for val in norm_values if val > threshold)
        return active >= min_active
    
    ## @brief Saves calibration data to a file.
    def save_calibration(self):
        try:
            with open(self.calibration_file, "w") as f:
                for sensor in self.sensors:
                    f.write(f"{sensor.white},{sensor.black}\n")
            print("Calibration saved successfully.")
        except Exception as e:
            print(f"Error saving calibration: {e}")

    ## @brief Loads calibration data from a file.
    def load_calibration(self):
        try:
            with open(self.calibration_file, "r") as f:
                lines = f.readlines()
                if len(lines) == len(self.sensors):
                    for i, line in enumerate(lines):
                        white, black = map(int, line.strip().split(","))
                        self.sensors[i].white = white
                        self.sensors[i].black = black
                    print("Calibration loaded successfully.")
                else:
                    print("Calibration file mismatch. Recalibrate sensors.")
        except Exception as e:
            print(f"Error loading calibration: {e}")
