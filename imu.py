import pyb
from pyb import Pin, I2C
import struct

class BNO055:
    def __init__(self, i2c, address=0x28):
        self.i2c = i2c
        self.address = address
        self.center = None
        # Start in configuration mode
        self.set_mode(0x00)

    def set_mode(self, mode):
        """
        Set the operating mode of the BNO055.
        In this case, mode 0x0C (NDOF) uses the magnetometer for absolute heading.
        """
        try:
            # Ensure the sensor is in Normal mode (Power Mode register 0x3E)
            pyb.delay(100)
            self.i2c.mem_write(0x00, self.address, 0x3E)
            pyb.delay(100)
            # Write to the mode register (typically at 0x3D)
            self.i2c.mem_write(0x00, 0x28, 0x3D)
            pyb.delay(100)
            self.i2c.mem_write(mode, 0x28, 0x3D)
            pyb.delay(1000)  # Wait 1 second before checking again
            status = self.i2c.mem_read(1, 0x28, 0x39)
            print("Status is:"+str(status))
        except Exception as e:
            print("Error setting mode:", e)

    def get_calibration_status(self):
        """
        Retrieve and parse the calibration status byte.
        Returns a dictionary with 'sys', 'gyro', 'accel', and 'mag' calibration statuses.
        """
        try:
            # Read 1 byte from register 0x35 that holds calibration info
            calib = self.i2c.mem_read(1, self.address, 0x35)
            pyb.delay(1000)  # Wait 1 second before checking again

            calib_byte = calib[0]
            status = {
                'sys': (calib_byte >> 6) & 0x03,
                'gyro': (calib_byte >> 4) & 0x03,
                'accel': (calib_byte >> 2) & 0x03,
                'mag': calib_byte & 0x03
            }
            return status
        except Exception as e:
            print("Error reading calibration status:", e)
            return None

    def read_calibration_coefficients(self):
        """
        Read the calibration coefficients from the sensor.
        These are typically 22 bytes starting at register 0x55.
        """
        try:
            coeffs = self.i2c.mem_read(22, self.address, 0x55)
            return coeffs
        except Exception as e:
            print("Error reading calibration coefficients:", e)
            return None

    def write_calibration_coefficients(self, coeffs):
        """
        Write the provided calibration coefficients to the sensor.
        """
        try:
            for i, byte in enumerate(coeffs):
                self.i2c.mem_write(byte, self.address, 0x55 + i)
        except Exception as e:
            print("Error writing calibration coefficients:", e)
        self.set_mode(0x0C)
    def getMag(self):
        """
        Read the magnetometer data from the BNO055 sensor.
        The data is stored in registers 0x0E to 0x13.
        """
        try:
            
            # Read 6 bytes from register 0x0E
            data = self.i2c.mem_read(6, self.address, 0x0E)
            
            # Unpack the data as three 16-bit signed integers
            mag_x = struct.unpack('<h', data[0:2])[0]
            mag_y = struct.unpack('<h', data[2:4])[0]
            mag_z = struct.unpack('<h', data[4:6])[0]
            
            return (mag_x, mag_y, mag_z)
        except Exception as e:
            print("Error reading magnetometer data:", e)
            return (0, 0, 0)
        
    def getAccel(self):
        """
        Read the magnetometer data from the BNO055 sensor.
        The data is stored in registers 0x0E to 0x13.
        """
        try:
            
            # Read 6 bytes from register 0x0E
            data = self.i2c.mem_read(6, self.address, 0x08)
            
            # Unpack the data as three 16-bit signed integers
            mag_x = struct.unpack('<h', data[0:2])[0]
            mag_y = struct.unpack('<h', data[2:4])[0]
            mag_z = struct.unpack('<h', data[4:6])[0]
            
            return (mag_x, mag_y, mag_z)
        except Exception as e:
            print("Error reading magnetometer data:", e)
            return (0, 0, 0)
        

    def getGyr(self):
        try:
            
            # Read 6 bytes from register 0x0E
            data = self.i2c.mem_read(6, self.address, 0x14)
            
            # Unpack the data as three 16-bit signed integers
            mag_x = struct.unpack('<h', data[0:2])[0]
            mag_y = struct.unpack('<h', data[2:4])[0]
            mag_z = struct.unpack('<h', data[4:6])[0]
            
            return (mag_x, mag_y, mag_z)
        except Exception as e:
            print("Error reading magnetometer data:", e)
            return (0, 0, 0)
    
    def getEuler(self):
        try:
            
            # Read 6 bytes from register 0x0E
            data = self.i2c.mem_read(6, self.address, 0x1A)
            
            # Unpack the data as three 16-bit signed integers
            mag_x = struct.unpack('<h', data[0:2])[0]
            mag_y = struct.unpack('<h', data[2:4])[0]
            mag_z = struct.unpack('<h', data[4:6])[0]
            
            return (mag_x, mag_y, mag_z)
        except Exception as e:
            print("Error reading magnetometer data:", e)
            return (0, 0, 0)
    
    def save_calibration_to_file(self, filename="calibration.bin"):
        """Save calibration data to a file."""
        try:
            data = self.read_calibration_coefficients()
            if data:
                with open(filename, "wb") as f:
                    f.write(data)
                print("Calibration data saved.")
            else:
                print("Failed to read calibration data.")
        except Exception as e:
            print("Error saving calibration:", e)

    def load_calibration_from_file(self, filename="calibration.bin"):
        """Load and apply calibration data from a file."""
        try:
            with open(filename, "rb") as f:
                data = f.read()
            if len(data) == 22:
                self.write_calibration_coefficients(data)
                print("Calibration data restored.")
                self.setCenter()
                print("Center set to:", self.center)
            else:
                print("Invalid calibration file.")
        except OSError:
            print("No saved calibration file found.")

    def calibrate_imu(self):
        print("Starting IMU calibration procedure.")
        # Switch to fusion mode (e.g., NDOF mode) which uses the magnetometer.
        self.set_mode(0x0C)
        print("Please move the sensor in a figure-eight pattern to calibrate the magnetometer, "
            "and keep it steady for the accelerometer and gyroscope calibration.")
        i=0
        while True:
            status = self.get_calibration_status()
            
            if status:
                print("Calibration status: sys=%d, gyro=%d, accel=%d, mag=%d" %
                    (status['sys'], status['gyro'], status['accel'], status['mag']))
                
                # Check if all sensors are fully calibrated (each should read 3)
            if (status['sys'] == 3 and status['gyro'] == 3 and 
                status['accel'] == 3 and status['mag'] == 3):
                print("IMU calibration complete!")
                break

            i+=1
            pyb.delay(1000)  # Wait 1 second before checking again

    def setCenter(self):
        num_samples = 10
        total_heading = 0
        for _ in range(num_samples):
            total_heading += self.getEuler()[0]
        calibration_center = total_heading / num_samples
        print("Calibration center set to:", calibration_center)
        self.center = calibration_center
