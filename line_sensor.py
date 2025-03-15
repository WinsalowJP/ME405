from pyb import ADC, Pin, delay

class LineSensor:
    def __init__(self, pin, white=4095, black=0):
        # Initialize the ADC for the given pin.
        self.adc = ADC(Pin(pin))
        # Set calibration limits (default if no file is loaded).
        self.white = white  
        self.black = black  
    
    def read_raw(self):  # Read raw values from the line sensor
        return self.adc.read()
    
    def calibrate_value(self, sample):  # Calibrate values
        if sample < self.white:
            self.white = sample
        if sample > self.black:
            self.black = sample
    
    def normalize(self, raw):  # Normalize the value
        if (self.black - self.white) != 0:
            norm = (raw - self.white) / (self.black - self.white)
            return max(0, min(1, norm))
        else:
            return 0

class LineSensorArray:
    def __init__(self, pin_list):
        self.sensors = [LineSensor(pin) for pin in pin_list]
        self.calibration_file = "line_calibration.txt"
        self.load_calibration()  # Load calibration at startup
    
    def calibrate(self, samples=50, delay_ms=20):
        for _ in range(samples):
            for sensor in self.sensors:
                sample = sensor.read_raw()
                sensor.calibrate_value(sample)
            delay(delay_ms)
        self.save_calibration()  # Save after calibration
    
    def read_raw(self):
        return [sensor.read_raw() for sensor in self.sensors]
    
    def get_normalized_values(self):
        raw_values = self.read_raw()
        return [sensor.normalize(raw) for sensor, raw in zip(self.sensors, raw_values)]
    
    def compute_centroid(self):
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
        norm_values = self.get_normalized_values()
        active = sum(1 for val in norm_values if val > threshold)
        return active >= min_active
    
    def save_calibration(self):
        """Save the calibration values to a file."""
        try:
            with open(self.calibration_file, "w") as f:
                for sensor in self.sensors:
                    f.write(f"{sensor.white},{sensor.black}\n")
            print("Calibration saved successfully.")
        except Exception as e:
            print(f"Error saving calibration: {e}")

    def load_calibration(self):
        """Load the calibration values from a file."""
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

