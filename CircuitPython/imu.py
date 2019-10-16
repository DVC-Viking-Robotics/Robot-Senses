"""
IMU_Sensor
===========
"""
from math import pi as PI, atan2, degrees, sqrt
from serial import Serial, SerialException
from .common import SER_MGR

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
        self._ser = Serial(address)
        if self._ser is None:
            try:
                if baud < 0:
                    self._ser = Serial(address)
                else:
                    self._ser = Serial(address, baud)
                print('Successfully opened port', address, '@', baud, 'to Arduino device')
            except SerialException:
                raise ValueError('unable to open serial arduino device @ port {}'.format(address))

    def get_heading(self):
        """
        use this function to capture heading data from an arduino polling a MAG3110 magnetometer sensor over USB serial connection.
        """
        temp = ''
        with self._ser as ser:
            temp = ser.readline().strip().decode('utf-8').rsplit(',')
        if temp:
            return float(temp[0])
