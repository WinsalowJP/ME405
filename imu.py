## @file imu.py
#  This file provides an interface to the BNO055 sensor.
#  It includes methods to configure the sensor, read calibration data,
#  obtain sensor measurements (magnetometer, accelerometer, gyroscope, Euler angles),
#  and save/load calibration data.
#


import pyb
from pyb import Pin, I2C
import struct

## @brief Class to interface with the BNO055 sensor.
class BNO055:
    ## @brief Initializes the BNO055 sensor.
    #  @param i2c The I2C bus instance.
    #  @param address The I2C address (default is 0x28).
    def __init__(self, i2c, address=0x28):
        self.i2c = i2c
        self.address = address
        self.center = None
        # Start in configuration mode.
        self.set_mode(0x00)

    ## @brief Sets the operating mode of the sensor.
    #  @param mode The desired operating mode.
    def set_mode(self, mode):
        try:
            pyb.delay(100)
            self.i2c.mem_write(0x00, self.address, 0x3E)
            pyb.delay(100)
            self.i2c.mem_write(0x00, 0x28, 0x3D)
            pyb.delay(100)
            self.i2c.mem_write(mode, 0x28, 0x3D)
            pyb.delay(1000)
            status = self.i2c.mem_read(1, 0x28, 0x39)
            print("Status is:" + str(status))
        except Exception as e:
            print("Error setting mode:", e)

    ## @brief Retrieves the calibration status.
    #  @return A dictionary with calibration statuses for system, gyro, accel, and mag.
    def get_calibration_status(self):
        try:
            calib = self.i2c.mem_read(1, self.address, 0x35)
            pyb.delay(1000)
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

    ## @brief Reads the calibration coefficients.
    #  @return A bytes object with calibration coefficients, or None on error.
    def read_calibration_coefficients(self):
        try:
            coeffs = self.i2c.mem_read(22, self.address, 0x55)
            return coeffs
        except Exception as e:
            print("Error reading calibration coefficients:", e)
            return None

    ## @brief Writes calibration coefficients to the sensor.
    #  @param coeffs A bytes-like object containing the calibration coefficients.
    def write_calibration_coefficients(self, coeffs):
        try:
            for i, byte in enumerate(coeffs):
                self.i2c.mem_write(byte, self.address, 0x55 + i)
        except Exception as e:
            print("Error writing calibration coefficients:", e)
        self.set_mode(0x0C)

    ## @brief Reads magnetometer data.
    #  @return A tuple (mag_x, mag_y, mag_z) or (0, 0, 0) on error.
    def getMag(self):
        try:
            data = self.i2c.mem_read(6, self.address, 0x0E)
            mag_x = struct.unpack('<h', data[0:2])[0]
            mag_y = struct.unpack('<h', data[2:4])[0]
            mag_z = struct.unpack('<h', data[4:6])[0]
            return (mag_x, mag_y, mag_z)
        except Exception as e:
            print("Error reading magnetometer data:", e)
            return (0, 0, 0)
        
    ## @brief Reads accelerometer data.
    #  @return A tuple (accel_x, accel_y, accel_z) or (0, 0, 0) on error.
    def getAccel(self):
        try:
            data = self.i2c.mem_read(6, self.address, 0x08)
            accel_x = struct.unpack('<h', data[0:2])[0]
            accel_y = struct.unpack('<h', data[2:4])[0]
            accel_z = struct.unpack('<h', data[4:6])[0]
            return (accel_x, accel_y, accel_z)
        except Exception as e:
            print("Error reading accelerometer data:", e)
            return (0, 0, 0)
        
    ## @brief Reads gyroscope data.
    #  @return A tuple (gyr_x, gyr_y, gyr_z) or (0, 0, 0) on error.
    def getGyr(self):
        try:
            data = self.i2c.mem_read(6, self.address, 0x14)
            gyr_x = struct.unpack('<h', data[0:2])[0]
            gyr_y = struct.unpack('<h', data[2:4])[0]
            gyr_z = struct.unpack('<h', data[4:6])[0]
            return (gyr_x, gyr_y, gyr_z)
        except Exception as e:
            print("Error reading gyroscope data:", e)
            return (0, 0, 0)
    
    ## @brief Reads Euler angle data.
    #  @return A tuple (euler_x, euler_y, euler_z) or (0, 0, 0) on error.
    def getEuler(self):
        try:
            data = self.i2c.mem_read(6, self.address, 0x1A)
            euler_x = struct.unpack('<h', data[0:2])[0]
            euler_y = struct.unpack('<h', data[2:4])[0]
            euler_z = struct.unpack('<h', data[4:6])[0]
            return (euler_x, euler_y, euler_z)
        except Exception as e:
            print("Error reading Euler angle data:", e)
            return (0, 0, 0)
    
    ## @brief Saves calibration data to a file.
    #  @param filename The file name (default "calibration.bin").
    def save_calibration_to_file(self, filename="calibration.bin"):
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

    ## @brief Loads calibration data from a file and applies it.
    #  @param filename The file name (default "calibration.bin").
    def load_calibration_from_file(self, filename="calibration.bin"):
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

    ## @brief Calibrates the IMU sensor.
    def calibrate_imu(self):
        print("Starting IMU calibration procedure.")
        self.set_mode(0x0C)
        print("Please move the sensor in a figure-eight pattern to calibrate the magnetometer, "
              "and keep it steady for the accelerometer and gyroscope calibration.")
        i = 0
        while True:
            status = self.get_calibration_status()
            if status:
                print("Calibration status: sys=%d, gyro=%d, accel=%d, mag=%d" %
                      (status['sys'], status['gyro'], status['accel'], status['mag']))
                if (status['sys'] == 3 and status['gyro'] == 3 and 
                    status['accel'] == 3 and status['mag'] == 3):
                    print("IMU calibration complete!")
                    break
            i += 1
            pyb.delay(1000)
    
    ## @brief Sets the sensor's center based on averaged Euler angle readings.
    def setCenter(self):
        num_samples = 10
        total_heading = 0
        for _ in range(num_samples):
            total_heading += self.getEuler()[0]
        calibration_center = total_heading / num_samples
        print("Calibration center set to:", calibration_center)
        self.center = calibration_center
