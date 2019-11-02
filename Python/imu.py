from math import pi as PI, atan2, degrees, sqrt
from serial import Serial
from circuitpython_mpu6050 import MPU6050
from adafruit_lsm9ds1 import LSM9DS1_I2C
import socketio
import time
from .common import I2C_BUS, SERVER, is_connected

sio = socketio.Client()
DELINATION = 0

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

# NOTE change this according to your config
IMU = LSM9DS1_I2C(I2C_BUS, 0x1c, 0x6a)
# IMU = MPU6050(I2C_BUS)

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

def calc_heading(mag, declination=DELINATION):
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

@sio.on('DoFrequest', namespace='/imu')
def on_DoF_request():
    """This event fired when a websocket client a response to the server about IMU
    device's data. Specifically the accerometer, gyroscope, & magnetometer data."""
    # print('DoF sensor data sent')
    sio.emit('sensorDoF-response', get_imu_data())

@sio.on("connect", namespace="/imu")
def on_connect():
    """This event is fired when the client has connected to the server."""
    is_connected = True

@sio.on('disconnect', namespace='/imu')
def on_disconnect():
    """When the client is disconnected from the server. This event is for debug only as it does
    nothing with the sensor."""
    print('connection to server lost')
    is_connected = False

def send_imu_hypr():
    """This function will "emit" the latest IMU data's heading, yaw, pitch, & roll in a `dict`
    form."""
    yaw, pitch, roll = calc_yaw_pitch_roll(IMU.acceleration, IMU.gyro)
    sio.emit('imu', data={'heading': calc_heading(IMU.magnetic),
                          'yaw': yaw, 'pitch': pitch, 'roll': roll}, namespace='/imu')
def send_imu_data():
    """This function will "emit" the latest IMU data's accerometer, gyroscope, & magnetometer
    in a `dict` form."""
    senses = get_imu_data()
    sio.emit('imu', data={'accel': senses[0],
                          'gyro': senses[1], 'mag': senses[2]}, namespace='/imu')

if __name__ == '__main__':
    sio.connect(SERVER, namespaces=('/imu'))
    while is_connected:
        send_imu_hypr()
        time.sleep(1)
