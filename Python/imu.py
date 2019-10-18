"""
This module is meant to handle all functionality related to the supported IMU sensors.
"""
from math import pi as PI, atan2, degrees, sqrt
from serial import Serial
from circuitpython_mpu6050 import MPU6050
from adafruit_lsm9ds1 import LSM9DS1_I2C
from .common import I2C_BUS
from .sockets import sio

# instantiate the IMU sensor for use with web sockets
# NOTE change this according to your config
IMU = LSM9DS1_I2C(I2C_BUS, 0x1c, 0x6a)
# IMU = MPU6050(I2C_BUS)

@sio.on('sensorDoF')
def handle_DoF_request():
    """This event fired when a websocket client a response to the server about IMU
    device's data."""
    senses = get_imu_data()
    sio.emit('sensorDoF-response', senses)
    print('DoF sensor data sent')

def get_imu_data():
    """Returns a 2d array containing the following

    * ``senses[0] = accel[x, y, z]`` for accelerometer data
    * ``senses[1] = gyro[x, y, z]`` for gyroscope data
    * ``senses[2] = mag[x, y, z]`` for magnetometer data

    .. note:: Not all data may be aggregated depending on the IMU device connected to the robot.

    """
    senses = [
        [None, None, None],
        [None, None, None],
        [None, None, None]
    ]
    if getattr(IMU, 'acceleration') and callable(IMU.acceleration):
        senses[0] = list(IMU.acceleration)
    if getattr(IMU, 'gyro') and callable(IMU.gyro):
        senses[1] = list(IMU.gyro)
    if getattr(IMU, 'magnetic') and callable(IMU.magnetic):
        senses[2] = list(IMU.magnetic)
    return senses

def calc_heading(mag, declination=0):
    """This function calculates the course heading based on magnetometer data passed to it. You can optionally also specify your location's declination"""
    heading = 0
    if type(mag, (tuple, list)) and len(mag) == 3:
        if mag[0] == 0 and mag[1] < 0:
            heading = PI / 2
        else: heading = atan2(mag[1], mag[0])

        # Convert everything from radians to degrees:
        heading = degrees(heading)
        heading -= declination

        # ensure proper range of [0, 360]
        if heading > 360:
            heading -= 360
        elif heading < 0:
            heading += 360
        return heading
    raise ValueError('argument mag must be a list or tuple with a length of 3 values (1 for each axis)')
    # if 337.25 < heading < 22.5 == North
    # if 292.5 < heading < 337.25 == North-West
    # if 247.5 < heading < 292.5 == West
    # if 202.5 < heading < 247.5 == South-West
    # if 157.5 < heading < 202.5 == South
    # if 112.5 < heading < 157.5 == South-East
    # if 67.5 < heading < 112.5 == East
    # if 22.5 < heading < 67.5 == North-East

def calc_yaw_pitch_roll(accel, gyro):
    """
    calculate the orientation of the accelerometer and convert the output of atan2 from radians to degrees

    this data is used to correct any cumulative errors in the orientation that the gyroscope develops.

    """
    if type(accel, (tuple, list)) and type(gyro, (list, tuple)) and len(accel) == 3 and len(gyro) == 3:
        roll = degrees(atan2(accel[1], accel[2]))
        pitch = degrees(atan2(accel[0], sqrt(accel[1] * accel[1] + accel[2] * accel[2])))
        yaw = gyro[2]
        return (yaw, pitch, roll)
    raise ValueError('arguments must be a list or tuple of length 3 (1 for each axis)')

class MAG3110:
    """a class to gather data over USB from an Arduino connected to the Sparfun MAG3110 magnetometer sensor."""
    def __init__(self, address, baud=-1):
        if baud < 0:
            self._ser = Serial(address)
        else:
            self._ser = Serial(address, baud)
        # print('Successfully opened port {} @ {} to Arduino device'.format(address, baud))
        self._ser.close()

    def get_heading(self):
        """
        use this function to capture heading data from an arduino polling a MAG3110 magnetometer sensor over USB serial connection.
        """
        temp = ''
        with self._ser as ser:
            temp = ser.readline().strip().decode('utf-8').rsplit(',')
        if temp:
            return float(temp[0])
