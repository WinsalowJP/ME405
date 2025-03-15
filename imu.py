"""
@file imu.py
@brief Provides an interface to the BNO055 sensor for obtaining orientation, calibration,
       and sensor data including magnetometer, accelerometer, gyroscope, and Euler angles.

This module defines the BNO055 class, which handles configuration, calibration,
and data acquisition from the BNO055 sensor over I2C.
"""

import pyb
from pyb import Pin, I2C
import struct

class BNO055:
    """
    @brief A class to interface with the BNO055 sensor.

    The BNO055 class provides methods to configure the sensor's operating mode,
    read calibration status and coefficients, acquire sensor data (magnetometer,
    accelerometer, gyroscope, Euler angles), and save/load calibration data from a file.
    """
    
    def __init__(self, i2c, address=0x28):
        """
        @brief Initializes the BNO055 sensor interface.

        Configures the sensor to start in configuration mode and sets the I2C address.

        @param i2c The I2C bus instance used for communication with the sensor.
        @param address The I2C address of the BNO055 sensor (default is 0x28).
        """
        self.i2c = i2c
        self.address = address
        self.center = None
        # Start in configuration mode
        self.set_mode(0x00)

    def set_mode(self, mode):
        """
        @brief Sets the operating mode of the BNO055 sensor.

        In this example, mode 0x0C (NDOF) uses the magnetometer for absolute heading.
        The function writes to the power mode and mode registers with appropriate delays.

        @param mode The mode to set for the sensor.
        """
        try:
            # Ensure the sensor is in Normal mode (Power Mode register 0x3E)
            pyb.delay(100)
            self.i2c.mem_write(0x00, self.address, 0x3E)
            pyb.delay(100)
            # Write to the mode register (typically at 0x3D) to reset to configuration
            self.i2c.mem_write(0x00, 0x28, 0x3D)
            pyb.delay(100)
            self.i2c.mem_write(mode, 0x28, 0x3D)
            pyb.delay(1000)  # Wait 1 second before checking again
            status = self.i2c.mem_read(1, 0x28, 0x39)
            print("Status is:" + str(status))
        except Exception as e:
            print("Error setting mode:", e)

    def get_calibration_status(self):
        """
        @brief Retrieves and parses the calibration status of the sensor.

        Reads a single byte from the calibration register and extracts calibration
        levels for the system, gyroscope, accelerometer, and magnetometer.

        @return A dictionary with keys 'sys', 'gyro', 'accel', and 'mag' indicating the
                calibration statuses, or None if an error occurs.
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
        @brief Reads the calibration coefficients from the sensor.

        Typically, 22 bytes are read starting from register 0x55.

        @return A bytes object containing the calibration coefficients, or None if an error occurs.
        """
        try:
            coeffs = self.i2c.mem_read(22, self.address, 0x55)
            return coeffs
        except Exception as e:
            print("Error reading calibration coefficients:", e)
            return None

    def write_calibration_coefficients(self, coeffs):
        """
        @brief Writes calibration coefficients to the sensor.

        Writes each byte from the provided coefficients to consecutive registers starting at 0x55.
        After writing, the sensor mode is set to 0x0C (NDOF).

        @param coeffs A bytes-like object containing the calibration coefficients.
        """
        try:
            for i, byte in enumerate(coeffs):
                self.i2c.mem_write(byte, self.address, 0x55 + i)
        except Exception as e:
            print("Error writing calibration coefficients:", e)
        self.set_mode(0x0C)

    def getMag(self):
        """
        @brief Reads magnetometer data from the sensor.

        Reads 6 bytes starting at register 0x0E and unpacks them into three 16-bit signed integers.

        @return A tuple (mag_x, mag_y, mag_z) representing the magnetometer readings, or (0, 0, 0) on error.
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
        @brief Reads accelerometer data from the sensor.

        Reads 6 bytes starting at register 0x08 and unpacks them into three 16-bit signed integers.

        @return A tuple (accel_x, accel_y, accel_z) representing the accelerometer readings,
                or (0, 0, 0) on error.
        """
        try:
            # Read 6 bytes from register 0x08
            data = self.i2c.mem_read(6, self.address, 0x08)
            
            # Unpack the data as three 16-bit signed integers
            accel_x = struct.unpack('<h', data[0:2])[0]
            accel_y = struct.unpack('<h', data[2:4])[0]
            accel_z = struct.unpack('<h', data[4:6])[0]
            
            return (accel_x, accel_y, accel_z)
        except Exception as e:
            print("Error reading accelerometer data:", e)
            return (0, 0, 0)
        
    def getGyr(self):
        """
        @brief Reads gyroscope data from the sensor.

        Reads 6 bytes starting at register 0x14 and unpacks them into three 16-bit signed integers.

        @return A tuple (gyr_x, gyr_y, gyr_z) representing the gyroscope readings,
                or (0, 0, 0) on error.
        """
        try:
            # Read 6 bytes from register 0x14
            data = self.i2c.mem_read(6, self.address, 0x14)
            
            # Unpack the data as three 16-bit signed integers
            gyr_x = struct.unpack('<h', data[0:2])[0]
            gyr_y = struct.unpack('<h', data[2:4])[0]
            gyr_z = struct.unpack('<h', data[4:6])[0]
            
            return (gyr_x, gyr_y, gyr_z)
        except Exception as e:
            print("Error reading gyroscope data:", e)
            return (0, 0, 0)
    
    def getEuler(self):
        """
        @brief Reads Euler angle data from the sensor.

        Reads 6 bytes starting at register 0x1A and unpacks them into three 16-bit signed integers.

        @return A tuple (euler_x, euler_y, euler_z) representing the Euler angles,
                or (0, 0, 0) on error.
        """
        try:
            # Read 6 bytes from register 0x1A
            data = self.i2c.mem_read(6, self.address, 0x1A)
            
            # Unpack the data as three 16-bit signed integers
            euler_x = struct.unpack('<h', data[0:2])[0]
            euler_y = struct.unpack('<h', data[2:4])[0]
            euler_z = struct.unpack('<h', data[4:6])[0]
            
            return (euler_x, euler_y, euler_z)
        except Exception as e:
            print("Error reading Euler angle data:", e)
            return (0, 0, 0)
    
    def save_calibration_to_file(self, filename="calibration.bin"):
        """
        @brief Saves calibration data to a file.

        Reads the calibration coefficients from the sensor and writes them to a binary file.
        
        @param filename The name of the file to which calibration data is saved (default "calibration.bin").
        """
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
        """
        @brief Loads calibration data from a file and applies it to the sensor.

        Reads the calibration data from the specified file, writes the coefficients to the sensor,
        and then sets the sensor's center based on the Euler angle readings.

        @param filename The name of the file from which calibration data is loaded (default "calibration.bin").
        """
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
        """
        @brief Calibrates the IMU sensor.

        Initiates the calibration procedure by switching to fusion mode (NDOF mode) and prompting the user
        to move the sensor in a figure-eight pattern. Continuously checks the calibration status until all
        sensors are fully calibrated.
        """
        print("Starting IMU calibration procedure.")
        # Switch to fusion mode (e.g., NDOF mode) which uses the magnetometer.
        self.set_mode(0x0C)
        print("Please move the sensor in a figure-eight pattern to calibrate the magnetometer, "
              "and keep it steady for the accelerometer and gyroscope calibration.")
        i = 0
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

            i += 1
            pyb.delay(1000)  # Wait 1 second before checking again

    def setCenter(self):
        """
        @brief Sets the center value for sensor orientation.

        Averages multiple Euler angle readings to determine and set a calibration center.
        This value can be used for further sensor data adjustments.

        @note The center is computed as the average of the first Euler angle over 10 samples.
        """
        num_samples = 10
        total_heading = 0
        for _ in range(num_samples):
            total_heading += self.getEuler()[0]
        calibration_center = total_heading / num_samples
        print("Calibration center set to:", calibration_center)
        self.center = calibration_center
